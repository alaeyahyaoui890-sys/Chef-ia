"""Module interfaces and contracts for the Atelier des mondes kernel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModuleManifest:
    module_id: str
    name: str
    version: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    api_version: str = "1.0"
    enabled: bool = True
    capabilities: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errors = []
        if not self.module_id or not isinstance(self.module_id, str):
            errors.append("module_id required")
        if not self.name:
            errors.append("name required")
        if not self.version:
            errors.append("version required")
        if not self.api_version:
            errors.append("api_version required")
        # circular deps checked by manager
        if self.module_id in self.dependencies:
            errors.append("self dependency")
        return errors


class IModule(ABC):
    @abstractmethod
    def manifest(self) -> ModuleManifest:
        ...

    @abstractmethod
    def on_load(self, context: Any) -> None:
        ...

    @abstractmethod
    def on_start(self) -> None:
        ...

    @abstractmethod
    def on_stop(self) -> None:
        ...

    @abstractmethod
    def on_unload(self) -> None:
        ...


class IEvent(ABC):
    pass


class IService(ABC):
    pass
