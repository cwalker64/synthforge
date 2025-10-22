"""Tests for the rule-based repairer."""

from synthforge.eval.runner import best_result, evaluate
from synthforge.repair.base import RepairContext
from synthforge.repair.rules import RuleRepairer
from synthforge.types import Candidate, Task


def _task() -> Task:
    return Task(
        task_id="add",
        prompt="add two numbers",
        entry_point="add",
        tests=("assert add(2, 3) == 5", "assert add(10, 5) == 15"),
    )


def test_repairer_produces_a_passing_variant() -> None:
    task = _task()
    buggy = Candidate("def add(a, b):\n    return a - b\n")
    result = evaluate(task, buggy)
    assert not result.passed

    variants = RuleRepairer().repair(RepairContext(task, buggy, result))
    fixed = best_result(evaluate(task, v) for v in variants)
    assert fixed is not None
    assert fixed.passed


def test_repairer_excludes_original() -> None:
    task = _task()
    buggy = Candidate("def add(a, b):\n    return a - b\n")
    result = evaluate(task, buggy)
    variants = RuleRepairer().repair(RepairContext(task, buggy, result))
    assert all(v.source != buggy.source for v in variants)


def test_repairer_respects_variant_cap() -> None:
    task = _task()
    buggy = Candidate("def add(a, b):\n    return a - b + 1 - 2 + 3\n")
    result = evaluate(task, buggy)
    variants = RuleRepairer(max_variants=3).repair(RepairContext(task, buggy, result))
    assert len(variants) <= 3
