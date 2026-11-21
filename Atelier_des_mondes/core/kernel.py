"""Central kernel: orchestrates all core subsystems."""

from __future__ import annotations

import os
from typing import Any

from core.logging_system import KernelLogger
from core.event_bus import EventBus
from core.service_registry import ServiceRegistry
from core.module_manager import ModuleManager
from core.resource_manager import ResourceManager
from core.task_manager import TaskManager
from core.memory_manager import MemoryManager
from core.settings_manager import SettingsManager
from core.database import Database
from core.migrations import MigrationManager
from core.project_manager import ProjectManager
from core.backup_manager import BackupManager
from core.diagnostics import Diagnostics
from core.context import KernelContext


class Kernel:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.logger = KernelLogger(os.path.join(self.data_dir, "logs"))
        self.settings = SettingsManager(os.path.join(self.data_dir, "settings"), self.logger)
        self.db = Database(os.path.join(self.data_dir, "database", "app.db"))
        self.migrations = MigrationManager(self.db, self.logger)
        self.events = EventBus(self.logger)
        self.services = ServiceRegistry(self.logger)
        self.resources = ResourceManager(os.path.join(self.data_dir, "resources"), self.logger)
        self.memory = MemoryManager(self.logger, self.settings.get("memory_limit_mb", 4096))
        self.tasks = TaskManager(self.logger)
        self.backup = BackupManager(self.data_dir, self.db, self.logger)
        self.projects = ProjectManager(self.db, self.data_dir, self.logger, self.backup)
        self.module_manager = ModuleManager(self.logger, self.events)
        self.diagnostics = Diagnostics(self)
        self._context = KernelContext(
            kernel=self, logger=self.logger, settings=self.settings,
            resources=self.resources, events=self.events, services=self.services,
            tasks=self.tasks, storage=self.db, project_manager=self.projects,
            backup=self.backup,
        )

    def context(self):
        return self._context

    def start(self):
        self.logger.info("kernel", "Starting kernel")
        self.migrations.migrate_to(self.migrations.latest())
        self.module_manager.start_all(self._context)
        self.events.publish("kernel.started")
        self.logger.info("kernel", "Kernel started")

    def stop(self):
        self.logger.info("kernel", "Stopping kernel")
        self.module_manager.stop_all()
        self.db.close()
        self.events.publish("kernel.stopped")
        self.logger.info("kernel", "Kernel stopped")

    def register_module(self, instance):
        return self.module_manager.register(instance)

    def status(self):
        return self.module_manager.status()
