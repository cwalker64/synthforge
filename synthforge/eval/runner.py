"""Map tasks and candidates onto the sandbox and back to domain types."""

from __future__ import annotations

from typing import Optional

from synthforge.eval.sandbox import SandboxOutcome, run_in_sandbox
from synthforge.types import Candidate, EvalResult, Task, TestOutcome


def evaluate(task: Task, candidate: Candidate, *, timeout: Optional[float] = None) -> EvalResult:
    """Run ``candidate`` against every test in ``task`` and score it."""
    limit = task.timeout if timeout is None else timeout
    sandbox = run_in_sandbox(
        candidate.source,
        list(task.tests),
        setup=task.setup,
        timeout=limit,
    )
    return _to_result(task, candidate, sandbox)


def _to_result(task: Task, candidate: Candidate, sandbox: SandboxOutcome) -> EvalResult:
    outcomes = tuple(
        TestOutcome(
            index=int(raw["index"]),
            passed=bool(raw["passed"]),
            error=raw.get("error"),
            duration=float(raw.get("duration", 0.0)),
        )
        for raw in sandbox.outcomes
    )
    return EvalResult(
        task_id=task.task_id,
        candidate=candidate,
        outcomes=outcomes,
        timed_out=sandbox.timed_out,
        duration=sandbox.duration,
    )
