"""Module manager: registration, dependencies, lifecycle, states."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from interfaces.module_interface import ModuleManifest


class ModuleState(str, Enum):
    REGISTERED = "Enregistré"
    PENDING = "En attente"
    INITIALIZING = "Initialisation"
    ACTIVE = "Actif"
    FAILED = "Défaillant"
    BLOCKED = "Bloqué"
    DISABLED = "Désactivé"
    STOPPED = "Arrêté"


@dataclass
class ModuleRecord:
    module_id: str
    manifest: ModuleManifest
    instance: Any
    state: ModuleState = ModuleState.REGISTERED
    error: Optional[str] = None


class ModuleManager:
    def __init__(self, logger, event_bus):
        self.logger = logger
        self.event_bus = event_bus
        self._modules: Dict[str, ModuleRecord] = {}
        self._lock = threading.RLock()

    def register(self, instance) -> bool:
        m = instance.manifest()
        errs = m.validate()
        if errs:
            self.logger.error("module_manager", f"Invalid manifest {m.module_id}: {errs}")
            return False
        if m.module_id in self._modules:
            self.logger.error("module_manager", f"Duplicate module id {m.module_id}")
            return False
        # circular dep check
        if self._has_circular(m.module_id, m.dependencies):
            self.logger.error("module_manager", f"Circular dependency for {m.module_id}")
            return False
        # dependency existence
        for dep in m.dependencies:
            if dep not in self._modules:
                # allow pending
                pass
        rec = ModuleRecord(m.module_id, m, instance, ModuleState.REGISTERED)
        self._modules[m.module_id] = rec
        self.logger.info("module_manager", f"Registered {m.module_id}")
        return True

    def _has_circular(self, mid, deps, seen=None):
        if seen is None:
            seen = set()
        for d in deps:
            if d == mid:
                return True
            if d in self._modules:
                if d in seen:
                    return True
                seen.add(d)
                if self._has_circular(mid, self._modules[d].manifest.dependencies, seen):
                    return True
        return False

    def start_all(self, context):
        # topological order
        order = self._topological_order()
        for mid in order:
            rec = self._modules[mid]
            if not rec.manifest.enabled:
                rec.state = ModuleState.DISABLED
                continue
            # check deps
            blocked = False
            for dep in rec.manifest.dependencies:
                if dep not in self._modules or self._modules[dep].state not in (ModuleState.ACTIVE, ModuleState.DISABLED):
                    if dep in self._modules and self._modules[dep].state == ModuleState.FAILED:
                        blocked = True
            if blocked:
                rec.state = ModuleState.BLOCKED
                continue
            # pending if deps not active yet (shouldn't with topo)
            try:
                rec.state = ModuleState.INITIALIZING
                rec.instance.on_load(context)
                rec.instance.on_start()
                rec.state = ModuleState.ACTIVE
                self.logger.info("module_manager", f"Started {mid}")
            except Exception as e:
                rec.state = ModuleState.FAILED
                rec.error = str(e)
                self.logger.error("module_manager", f"Failed to start {mid}: {e}")
                self.event_bus.publish("module.failed", {"module_id": mid, "error": str(e)})

    def _topological_order(self):
        visited = set()
        result = []
        def visit(mid):
            if mid in visited:
                return
            if mid not in self._modules:
                return
            for dep in self._modules[mid].manifest.dependencies:
                visit(dep)
            visited.add(mid)
            result.append(mid)
        for mid in list(self._modules.keys()):
            visit(mid)
        return result

    def stop_all(self):
        for mid in reversed(self._topological_order()):
            rec = self._modules.get(mid)
            if rec is None:
                continue
            try:
                if rec.state == ModuleState.ACTIVE:
                    rec.instance.on_stop()
                    rec.instance.on_unload()
                rec.state = ModuleState.STOPPED
            except Exception as e:
                rec.state = ModuleState.FAILED
                rec.error = str(e)
                self.logger.error("module_manager", f"Error stopping {mid}: {e}")

    def disable(self, mid):
        rec = self._modules.get(mid)
        if rec:
            try:
                if rec.state == ModuleState.ACTIVE:
                    rec.instance.on_stop()
                rec.state = ModuleState.DISABLED
            except Exception as e:
                rec.state = ModuleState.FAILED
                rec.error = str(e)

    def enable(self, mid, context):
        rec = self._modules.get(mid)
        if rec:
            try:
                rec.state = ModuleState.INITIALIZING
                rec.instance.on_load(context)
                rec.instance.on_start()
                rec.state = ModuleState.ACTIVE
            except Exception as e:
                rec.state = ModuleState.FAILED
                rec.error = str(e)

    def remove(self, mid):
        rec = self._modules.get(mid)
        if rec:
            try:
                if rec.state == ModuleState.ACTIVE:
                    rec.instance.on_stop()
                    rec.instance.on_unload()
            except Exception:
                pass
            del self._modules[mid]

    def status(self):
        return {mid: (r.state.value, r.error) for mid, r in self._modules.items()}

    def get(self, mid):
        return self._modules.get(mid)
