"""Loading and validating task suites.

For now this only defines the in-memory container. JSONL loading and field
validation are added in later changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from synthforge.types import Task


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
