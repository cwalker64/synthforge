"""Tests for the template synthesizer."""

from __future__ import annotations

from synthforge.eval.runner import evaluate
from synthforge.synth.template import TemplateSynthesizer, infer_kind, parse_signature
from synthforge.types import Candidate, Task


def test_parse_signature_extracts_params() -> None:
    name, params = parse_signature("def add(a, b):", "add")
    assert name == "add"
    assert params == ["a", "b"]


def test_infer_kind_from_prompt() -> None:
    assert infer_kind("return the sum of two numbers") == "sum"
    assert infer_kind("give back the input unchanged") == "identity"


def test_template_solves_addition() -> None:
    task = Task(
        task_id="add",
        prompt="return the sum of a and b",
        entry_point="add",
        tests=("assert add(2, 3) == 5",),
        signature="def add(a, b):",
    )
    best = _first_solution(task)
    assert best is not None


def test_template_solves_reverse() -> None:
    task = Task(
        task_id="rev",
        prompt="return the string reversed",
        entry_point="rev",
        tests=('assert rev("abc") == "cba"',),
        signature="def rev(s):",
    )
    assert _first_solution(task) is not None


def _first_solution(task: Task) -> Candidate | None:
    synth = TemplateSynthesizer()
    for cand in synth.synthesize(task, n=len(_all_kinds())):
        if evaluate(task, cand).passed:
            return cand
    return None


def _all_kinds() -> list[str]:
    from synthforge.synth.template import TEMPLATES

    return list(TEMPLATES)
