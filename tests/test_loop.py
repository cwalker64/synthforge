"""End-to-end tests for the control loop, fully offline."""

from synthforge.loop import LoopConfig, solve_task
from synthforge.synth.fixture import FixtureSynthesizer
from synthforge.synth.template import TemplateSynthesizer
from synthforge.types import Task


def _add_task() -> Task:
    return Task(
        task_id="add",
        prompt="return the sum of a and b",
        entry_point="add",
        tests=("assert add(2, 3) == 5", "assert add(0, 0) == 0"),
        signature="def add(a, b):",
    )


def test_template_synthesizer_solves_directly() -> None:
    report = solve_task(_add_task(), TemplateSynthesizer(), config=LoopConfig(samples=1))
    assert report.solved
    assert report.best is not None and report.best.passed


def test_repair_recovers_buggy_candidate() -> None:
    task = _add_task()
    synth = FixtureSynthesizer({"add": ["def add(a, b):\n    return a - b\n"]})
    report = solve_task(task, synth, config=LoopConfig(samples=1, repair_budget=3))
    assert report.solved
    assert report.repairs  # at least one repair round was recorded


def test_unsolvable_task_reports_failure() -> None:
    task = Task(
        task_id="const",
        prompt="totally underspecified",
        entry_point="mystery",
        tests=("assert mystery() == 42",),
    )
    synth = FixtureSynthesizer({"const": ["def mystery():\n    return 0\n"]})
    report = solve_task(task, synth, config=LoopConfig(samples=1, repair_budget=2))
    assert not report.solved
    assert report.best is not None
