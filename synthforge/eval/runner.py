"""Map tasks and candidates onto the sandbox and back to domain types."""

from __future__ import annotations

from collections.abc import Iterable

from synthforge.eval.sandbox import SandboxOutcome, run_in_sandbox
from synthforge.types import Candidate, EvalResult, Task, TestOutcome

# Prepended to every candidate so runs are deterministic and cannot block on
# interactive input. Kept tiny on purpose - the real isolation is the sandbox.
_HARNESS_PREAMBLE = (
    "import random as _sf_random\n"
    "_sf_random.seed(0)\n"
    "def input(*_a, **_k):\n"
    "    raise RuntimeError('input() is disabled during evaluation')\n"
)


def evaluate(task: Task, candidate: Candidate, *, timeout: float | None = None) -> EvalResult:
    """Run ``candidate`` against every test in ``task`` and score it."""
    limit = task.timeout if timeout is None else timeout
    setup = f"{_HARNESS_PREAMBLE}{task.setup}" if task.setup else _HARNESS_PREAMBLE
    sandbox = run_in_sandbox(
        candidate.source,
        list(task.tests),
        setup=setup,
        timeout=limit,
    )
    return _to_result(task, candidate, sandbox)


def evaluate_candidates(
    task: Task,
    candidates: Iterable[Candidate],
    *,
    timeout: float | None = None,
) -> list[EvalResult]:
    """Evaluate several candidates against a task, in order."""
    return [evaluate(task, c, timeout=timeout) for c in candidates]


def best_result(results: Iterable[EvalResult]) -> EvalResult | None:
    """Pick the strongest result: solved first, then by pass rate."""
    results = list(results)
    if not results:
        return None
    return max(results, key=lambda r: (r.passed, r.pass_rate, -r.duration))


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
