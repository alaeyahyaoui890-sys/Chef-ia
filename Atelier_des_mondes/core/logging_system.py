"""Centralized logging system."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional


class KernelLogger:
    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def __init__(self, log_dir: str, level: str = "INFO"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        self.level = level
        self._logger = logging.getLogger("atelier")
        self._logger.setLevel(self.LEVELS.get(level, 20))
        self._logger.handlers.clear()
        fh = logging.FileHandler(os.path.join(log_dir, "kernel.log"), encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        self._logger.addHandler(fh)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self._logger.addHandler(ch)

    def log(self, level: str, module: str, message: str, details: Optional[str] = None):
        lvl = self.LEVELS.get(level.upper(), 20)
        text = f"[{module}] {message}"
        if details:
            text += f" | {details}"
        self._logger.log(lvl, text)

    def debug(self, module, msg, details=None): self.log("DEBUG", module, msg, details)
    def info(self, module, msg, details=None): self.log("INFO", module, msg, details)
    def warning(self, module, msg, details=None): self.log("WARNING", module, msg, details)
    def error(self, module, msg, details=None): self.log("ERROR", module, msg, details)
    def critical(self, module, msg, details=None): self.log("CRITICAL", module, msg, details)

    def diagnostic_report(self) -> str:
        path = os.path.join(self.log_dir, "kernel.log")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()[-20000:]
        except Exception as e:
            return f"Unable to read log: {e}"
