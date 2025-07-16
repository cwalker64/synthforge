"""Loading and validating task suites.

Tasks can be built from plain dictionaries (e.g. decoded JSON) via
:func:`task_from_dict`, which checks the required fields are present and
well-typed before constructing a :class:`~synthforge.types.Task`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from synthforge.errors import TaskError
from synthforge.types import Task

_REQUIRED = ("task_id", "prompt", "entry_point", "tests")


def task_from_dict(data: Mapping[str, Any]) -> Task:
    """Build and validate a :class:`Task` from a mapping."""
    missing = [key for key in _REQUIRED if key not in data]
    if missing:
        raise TaskError(f"task is missing required fields: {', '.join(missing)}")

    tests = data["tests"]
    if not isinstance(tests, (list, tuple)) or not tests:
        raise TaskError(f"task {data['task_id']!r} must define a non-empty 'tests' list")
    if not all(isinstance(t, str) for t in tests):
        raise TaskError(f"task {data['task_id']!r} has a non-string test snippet")

    return Task(
        task_id=str(data["task_id"]),
        prompt=str(data["prompt"]),
        entry_point=str(data["entry_point"]),
        tests=tuple(tests),
        signature=data.get("signature"),
        setup=str(data.get("setup", "")),
        reference=data.get("reference"),
        hints=dict(data.get("hints", {})),
        timeout=float(data.get("timeout", 5.0)),
    )


@dataclass
class TaskSuite:
    """An ordered collection of tasks with fast lookup by id."""

    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._by_id = {t.task_id: t for t in self.tasks}

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self) -> int:
        return len(self.tasks)

    def get(self, task_id: str) -> Task:
        return self._by_id[task_id]
