"""The synth -> eval -> repair control loop.

:func:`solve_task` ties the three components together for a single task and
records everything that happened into a :class:`~synthforge.types.RunReport`.
This first cut only synthesizes and evaluates; the repair stage is layered on
top in a later change.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthforge.eval.runner import best_result, evaluate
from synthforge.synth.base import Synthesizer
from synthforge.types import RunReport, Task


@dataclass
class LoopConfig:
    """Knobs for a single :func:`solve_task` call."""

    samples: int = 1
    repair_budget: int = 3
    timeout: float | None = None


def solve_task(
    task: Task,
    synthesizer: Synthesizer,
    *,
    config: LoopConfig | None = None,
) -> RunReport:
    """Synthesize candidates for ``task`` and evaluate them."""
    config = config or LoopConfig()
    report = RunReport(task_id=task.task_id)

    candidates = synthesizer.synthesize(task, n=config.samples)
    for candidate in candidates:
        result = evaluate(task, candidate, timeout=config.timeout)
        report.attempts.append(result)
        if result.passed:
            return report

    # Nothing passed outright; the repair stage (added later) starts from here.
    _ = best_result(report.attempts)
    return report
