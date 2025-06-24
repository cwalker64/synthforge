"""The :class:`Synthesizer` protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from synthforge.types import Candidate, Task


@runtime_checkable
class Synthesizer(Protocol):
    """Produces candidate programs for a task.

    Implementations must be deterministic given the same ``task`` and ``n`` so
    that evaluation results are reproducible. ``name`` is used in reports and by
    the registry.
    """

    name: str

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        """Return up to ``n`` candidate solutions for ``task``."""
        ...
