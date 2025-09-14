"""Tests for the fixture synthesizer."""

from synthforge.synth.fixture import FixtureSynthesizer
from synthforge.types import Task


def _task(**hints) -> Task:
    return Task(
        task_id="demo",
        prompt="p",
        entry_point="f",
        tests=("assert f() == 1",),
        hints=hints,
    )


def test_fixture_from_bank_is_deterministic() -> None:
    synth = FixtureSynthesizer({"demo": ["def f():\n    return 1\n"]})
    first = synth.synthesize(_task(), n=1)
    second = synth.synthesize(_task(), n=1)
    assert first[0].source == second[0].source
    assert first[0].origin == "fixture"


def test_fixture_respects_n() -> None:
    synth = FixtureSynthesizer({"demo": ["a", "b", "c"]})
    assert len(synth.synthesize(_task(), n=2)) == 2


def test_fixture_falls_back_to_task_hints() -> None:
    synth = FixtureSynthesizer()
    candidates = synth.synthesize(_task(candidates=["def f():\n    return 1\n"]))
    assert candidates[0].source.strip().endswith("return 1")


def test_fixture_add_extends_bank() -> None:
    synth = FixtureSynthesizer()
    synth.add("demo", ["def f():\n    return 1\n"])
    assert synth.synthesize(_task())
