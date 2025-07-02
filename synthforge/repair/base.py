"""The :class:`Repairer` protocol and its feedback object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from synthforge.types import Candidate, EvalResult, Task


@dataclass
class RepairContext:
    """Feedback handed to a repairer after a failed evaluation."""

    task: Task
    candidate: Candidate
    result: EvalResult

    @property
    def error(self) -> str | None:
        return self.result.first_error()


@runtime_checkable
class Repairer(Protocol):
    """Attempts to fix a candidate given evaluation feedback."""

    name: str

    def repair(self, ctx: RepairContext) -> list[Candidate]:
        """Return zero or more repaired candidates to re-evaluate."""
        ...
