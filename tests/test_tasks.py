"""Tests for the tasks module."""

from synthforge.tasks import TaskSuite
from synthforge.types import Task


def _task(task_id: str = "t0") -> Task:
    return Task(
        task_id=task_id,
        prompt="return the input unchanged",
        entry_point="identity",
        tests=("assert identity(1) == 1",),
    )


def test_suite_lookup_by_id() -> None:
    suite = TaskSuite([_task("a"), _task("b")])
    assert len(suite) == 2
    assert suite.get("b").task_id == "b"
