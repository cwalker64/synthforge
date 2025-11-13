"""The synth -> eval -> repair control loop.

:func:`solve_task` ties the three components together for a single task and
records everything that happened into a :class:`~synthforge.types.RunReport`.
This first cut only synthesizes and evaluates; the repair stage is layered on
top in a later change.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthforge.eval.runner import best_result, evaluate
from synthforge.repair.base import RepairContext, Repairer
from synthforge.repair.rules import RuleRepairer
from synthforge.synth.base import Synthesizer
from synthforge.types import EvalResult, RepairStep, RunReport, Task


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
    repairer: Repairer | None = None,
    config: LoopConfig | None = None,
) -> RunReport:
    """Synthesize, evaluate, then iteratively repair until solved or exhausted."""
    config = config or LoopConfig()
    repairer = repairer if repairer is not None else RuleRepairer()
    report = RunReport(task_id=task.task_id)

    candidates = synthesizer.synthesize(task, n=config.samples)
    for candidate in candidates:
        result = evaluate(task, candidate, timeout=config.timeout)
        report.attempts.append(result)
        if result.passed:
            return report

    current = best_result(report.attempts)
    for iteration in range(1, config.repair_budget + 1):
        if current is None:
            break
        improved = _repair_once(task, current, repairer, report, iteration, config)
        if improved is None:
            break  # no repaired variant improved on the current best
        current = improved
        if current.passed:
            break
    return report


def _repair_once(
    task: Task,
    current: EvalResult,
    repairer: Repairer,
    report: RunReport,
    iteration: int,
    config: LoopConfig,
) -> EvalResult | None:
    """Run one repair round; return the new best result if it improved."""
    ctx = RepairContext(task, current.candidate, current)
    variants = repairer.repair(ctx)
    if not variants:
        return None

    round_results = [evaluate(task, v, timeout=config.timeout) for v in variants]
    report.attempts.extend(round_results)

    best = best_result(round_results)
    if best is None:
        return None
    report.repairs.append(
        RepairStep(
            iteration=iteration,
            operator=str(best.candidate.metadata.get("operator", "unknown")),
            before=current.candidate,
            after=best.candidate,
            result=best,
            improved=best.passed or best.pass_rate > current.pass_rate,
        )
    )
    if best.passed or best.pass_rate > current.pass_rate:
        return best
    return None

