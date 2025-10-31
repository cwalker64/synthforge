"""Tests for the tasks module."""

import pytest

from synthforge.errors import SuiteLoadError, TaskError
from synthforge.tasks import TaskSuite, load_suite, task_from_dict
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


def test_task_from_dict_roundtrip() -> None:
    task = task_from_dict(
        {
            "task_id": "add",
            "prompt": "add two numbers",
            "entry_point": "add",
            "tests": ["assert add(1, 2) == 3"],
        }
    )
    assert task.entry_point == "add"
    assert task.num_tests == 1


def test_task_from_dict_missing_field() -> None:
    with pytest.raises(TaskError):
        task_from_dict({"task_id": "x", "prompt": "p"})


def test_task_from_dict_empty_tests() -> None:
    with pytest.raises(TaskError):
        task_from_dict({"task_id": "x", "prompt": "p", "entry_point": "f", "tests": []})


def test_load_suite_from_jsonl(tmp_path) -> None:
    path = tmp_path / "suite.jsonl"
    path.write_text(
        '{"task_id": "a", "prompt": "p", "entry_point": "f", "tests": ["assert f() == 1"]}\n',
        encoding="utf-8",
    )
    suite = load_suite(path)
    assert len(suite) == 1
    assert suite.get("a").entry_point == "f"


def test_load_suite_rejects_empty(tmp_path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(SuiteLoadError):
        load_suite(path)
