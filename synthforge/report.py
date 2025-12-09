"""Human- and machine-readable rendering of run reports."""

from __future__ import annotations

from synthforge.types import RunReport


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
