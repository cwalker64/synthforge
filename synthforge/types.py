"""Core data structures shared across synthforge.

These are intentionally plain dataclasses with no behaviour beyond a few
convenience properties, so they can be passed between the synthesizer, the
evaluator and the repair loop without coupling those components together.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    """A single program-synthesis problem.

    ``tests`` are standalone Python snippets that exercise ``entry_point`` and
    raise (typically via ``assert``) on failure. A candidate solution is the
    body of the function named by ``entry_point``; the evaluator concatenates
    the candidate, any ``setup`` preamble and each test snippet before running.
    """

    task_id: str
    prompt: str
    entry_point: str
    tests: tuple[str, ...]
    signature: str | None = None
    setup: str = ""
    reference: str | None = None
    hints: dict[str, Any] = field(default_factory=dict)
    timeout: float = 5.0

    @property
    def num_tests(self) -> int:
        return len(self.tests)


@dataclass
class Candidate:
    """A proposed solution to a :class:`Task`."""

    source: str
    origin: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestOutcome:
    """Result of running one test snippet against a candidate."""

    index: int
    passed: bool
    error: str | None = None
    duration: float = 0.0


@dataclass
class EvalResult:
    """Outcome of evaluating a candidate against a whole task."""

    task_id: str
    candidate: Candidate
    outcomes: tuple[TestOutcome, ...]
    timed_out: bool = False
    duration: float = 0.0

    @property
    def num_tests(self) -> int:
        return len(self.outcomes)

    @property
    def num_passed(self) -> int:
        return sum(1 for o in self.outcomes if o.passed)

    @property
    def passed(self) -> bool:
        return self.num_tests > 0 and self.num_passed == self.num_tests

    @property
    def pass_rate(self) -> float:
        if not self.outcomes:
            return 0.0
        return self.num_passed / self.num_tests

    def first_error(self) -> str | None:
        for outcome in self.outcomes:
            if not outcome.passed and outcome.error:
                return outcome.error
        return None


@dataclass
class RepairStep:
    """One iteration of the repair loop."""

    iteration: int
    operator: str
    before: Candidate
    after: Candidate
    result: EvalResult
    improved: bool


@dataclass
class RunReport:
    """Everything that happened while solving a single task."""

    task_id: str
    attempts: list[EvalResult] = field(default_factory=list)
    repairs: list[RepairStep] = field(default_factory=list)

    @property
    def solved(self) -> bool:
        return any(a.passed for a in self.attempts)

    @property
    def best(self) -> EvalResult | None:
        if not self.attempts:
            return None
        return max(self.attempts, key=lambda a: (a.passed, a.pass_rate))
