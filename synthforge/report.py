"""Human- and machine-readable rendering of run reports."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from synthforge.types import EvalResult, RunReport


def render_text(report: RunReport) -> str:
    """Render a single run report as a short plain-text block."""
    status = "SOLVED" if report.solved else "FAILED"
    lines = [f"task {report.task_id}: {status}"]

    best = report.best
    if best is not None:
        lines.append(f"  best: {best.num_passed}/{best.num_tests} tests passing")
    lines.append(f"  attempts: {len(report.attempts)}  repair rounds: {len(report.repairs)}")

    if not report.solved and best is not None:
        error = best.first_error()
        if error:
            lines.append(f"  first error: {error}")
    return "\n".join(lines)


def _result_to_dict(result: EvalResult) -> dict[str, Any]:
    return {
        "origin": result.candidate.origin,
        "passed": result.passed,
        "num_passed": result.num_passed,
        "num_tests": result.num_tests,
        "pass_rate": result.pass_rate,
        "timed_out": result.timed_out,
    }


def report_to_dict(report: RunReport) -> dict[str, Any]:
    """Convert a run report into JSON-serialisable primitives."""
    best = report.best
    return {
        "task_id": report.task_id,
        "solved": report.solved,
        "num_attempts": len(report.attempts),
        "num_repairs": len(report.repairs),
        "best": _result_to_dict(best) if best is not None else None,
        "attempts": [_result_to_dict(a) for a in report.attempts],
    }


def render_json(report: RunReport, *, indent: int | None = 2) -> str:
    """Render a run report as a JSON document."""
    return json.dumps(report_to_dict(report), indent=indent)


def render_markdown(reports: Sequence[RunReport]) -> str:
    """Render a table of run reports as GitHub-flavoured Markdown."""
    header = "| task | status | tests | repairs |\n|------|--------|-------|---------|"
    rows = []
    for report in reports:
        best = report.best
        tests = f"{best.num_passed}/{best.num_tests}" if best is not None else "-"
        status = "pass" if report.solved else "fail"
        rows.append(f"| {report.task_id} | {status} | {tests} | {len(report.repairs)} |")
    return "\n".join([header, *rows])
