"""Diagnostics report generator."""

from __future__ import annotations

import os
import platform
import sys
from typing import Any


class Diagnostics:
    def __init__(self, kernel):
        self.kernel = kernel

    def report(self) -> str:
        lines = []
        lines.append("=== Atelier des mondes - Diagnostic ===")
        lines.append(f"Python: {sys.version}")
        lines.append(f"Platform: {platform.platform()}")
        lines.append(f"Modules: {self.kernel.module_manager.status()}")
        lines.append(f"Services: {self.kernel.services.list_services()}")
        lines.append(f"Memory usage MB: {self.kernel.memory.usage_mb():.2f}")
        lines.append(f"Settings: {self.kernel.settings.all()}")
        lines.append(f"DB version: {self.kernel.db.version()}")
        lines.append("Logs (tail):")
        lines.append(self.kernel.logger.diagnostic_report())
        return "\n".join(lines)
