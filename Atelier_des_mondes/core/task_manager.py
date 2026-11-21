"""Task manager: queued tasks, priorities, cancellation."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Any, Callable, Optional


@dataclass(order=True)
class Task:
    priority: int
    seq: int = field(compare=True)
    task_id: str = field(compare=False, default="")
    func: Callable = field(compare=False, default=None)
    args: tuple = field(compare=False, default=())
    kwargs: dict = field(compare=False, default_factory=dict)
    cancelled: bool = field(compare=False, default=False)


class TaskManager:
    def __init__(self, logger, max_concurrent: int = 2):
        self.logger = logger
        self.max_concurrent = max_concurrent
        self._q: PriorityQueue = PriorityQueue()
        self._seq = 0
        self._results: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._running = 0
        self._cond = threading.Condition(self._lock)

    def submit(self, func, *args, priority: int = 5, **kwargs) -> str:
        tid = str(uuid.uuid4())
        with self._lock:
            self._seq += 1
            t = Task(priority, self._seq, tid, func, args, kwargs)
            self._q.put(t)
        self.logger.info("task_manager", f"Submitted task {tid}")
        return tid

    def cancel(self, tid: str):
        # mark cancelled by draining? We'll store cancelled ids
        self._results[tid] = ("cancelled", None)

    def run_pending(self, max_tasks: int = 10):
        ran = 0
        while ran < max_tasks and not self._q.empty():
            t = self._q.get()
            if t.cancelled:
                continue
            try:
                res = t.func(*t.args, **t.kwargs)
                self._results[t.task_id] = ("done", res)
            except Exception as e:
                self._results[t.task_id] = ("error", str(e))
                self.logger.error("task_manager", f"Task {t.task_id} failed: {e}")
            ran += 1
        return ran

    def result(self, tid: str):
        return self._results.get(tid)
