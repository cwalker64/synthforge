"""Tests for the perturbation synthesizer."""

from __future__ import annotations

from synthforge.eval.runner import evaluate
from synthforge.synth.perturb import PerturbSynthesizer
from synthforge.types import Task


def _task(seed: str | None = None) -> Task:
    hints = {"seed": seed} if seed is not None else {}
    return Task(
        task_id="add",
        prompt="add two numbers",
        entry_point="add",
        tests=("assert add(2, 3) == 5",),
        hints=hints,
    )


def test_no_seed_yields_nothing() -> None:
    assert PerturbSynthesizer().synthesize(_task()) == []


def test_seed_is_first_candidate() -> None:
    seed = "def add(a, b):\n    return a - b\n"
    candidates = PerturbSynthesizer().synthesize(_task(seed), n=5)
    assert candidates[0].source == seed
    assert candidates[0].metadata["perturbation"] == "seed"


def test_perturbations_include_a_fix() -> None:
    seed = "def add(a, b):\n    return a - b\n"
    candidates = PerturbSynthesizer().synthesize(_task(seed), n=20)
    assert any(evaluate(_task(seed), c).passed for c in candidates)
