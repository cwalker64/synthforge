"""Shared pytest fixtures."""

import pytest

from synthforge.synth.template import TemplateSynthesizer
from synthforge.types import Candidate, Task


@pytest.fixture
def add_task() -> Task:
    """A simple, template-solvable addition task."""
    return Task(
        task_id="add",
        prompt="return the sum of a and b",
        entry_point="add",
        tests=("assert add(2, 3) == 5", "assert add(-1, 1) == 0"),
        signature="def add(a, b):",
    )


@pytest.fixture
def correct_add() -> Candidate:
    return Candidate("def add(a, b):\n    return a + b\n", origin="fixture")


@pytest.fixture
def template_synth() -> TemplateSynthesizer:
    return TemplateSynthesizer()
