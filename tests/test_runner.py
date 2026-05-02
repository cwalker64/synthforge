"""Tests for the evaluation runner."""

from synthforge.eval.runner import best_result, evaluate, evaluate_candidates
from synthforge.types import Candidate, Task


def _add_task() -> Task:
    return Task(
        task_id="add",
        prompt="add two integers",
        entry_point="add",
        tests=("assert add(1, 2) == 3", "assert add(-1, 1) == 0"),
    )


def test_evaluate_passing_candidate() -> None:
    task = _add_task()
    result = evaluate(task, Candidate("def add(a, b):\n    return a + b\n", origin="test"))
    assert result.passed
    assert result.num_passed == 2
    assert result.pass_rate == 1.0


def test_evaluate_partial_candidate() -> None:
    task = _add_task()
    # Correct for the first test only.
    result = evaluate(task, Candidate("def add(a, b):\n    return a + b if a > 0 else 99\n"))
    assert not result.passed
    assert 0 < result.pass_rate < 1


def test_best_result_prefers_solved() -> None:
    task = _add_task()
    results = evaluate_candidates(
        task,
        [
            Candidate("def add(a, b):\n    return a - b\n"),
            Candidate("def add(a, b):\n    return a + b\n"),
        ],
    )
    best = best_result(results)
    assert best is not None
    assert best.passed


def test_best_result_empty() -> None:
    assert best_result([]) is None


def test_timeout_marks_result_failed() -> None:
    task = Task(
        task_id="spin",
        prompt="loops forever",
        entry_point="spin",
        tests=("spin()",),
        timeout=1.0,
    )
    result = evaluate(task, Candidate("def spin():\n    while True:\n        pass\n"))
    assert result.timed_out
    assert not result.passed
