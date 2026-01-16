"""Command-line interface for synthforge.

``synthforge run`` synthesizes, evaluates and repairs a task suite offline and
prints a report. With no suite argument it uses the small bundled example.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from synthforge.config import RunConfig, load_config
from synthforge.loop import LoopConfig, solve_task
from synthforge.report import render_json, render_markdown, render_text
from synthforge.synth.registry import get_synthesizer
from synthforge.tasks import example_suite_path, load_suite
from synthforge.version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="synthforge", description=__doc__)
    parser.add_argument("--version", action="version", version=f"synthforge {__version__}")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run synth -> eval -> repair over a task suite")
    run.add_argument("suite", nargs="?", help="JSONL suite path (default: bundled example)")
    run.add_argument("-s", "--synthesizer", default="template", help="synthesizer name")
    run.add_argument("--samples", type=int, default=1, help="candidates per task")
    run.add_argument("--repair-budget", type=int, default=3, help="max repair rounds")
    run.add_argument("--timeout", type=float, default=5.0, help="per-test timeout (s)")
    run.add_argument("--config", help="config file (JSON or key: value)")
    run.add_argument(
        "-f",
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="output format",
    )
    run.set_defaults(func=_cmd_run)

    return parser


def _resolve_config(args: argparse.Namespace) -> RunConfig:
    if args.config:
        return load_config(args.config)
    return RunConfig(
        synthesizer=args.synthesizer,
        samples=args.samples,
        repair_budget=args.repair_budget,
        timeout=args.timeout,
    )


def _cmd_run(args: argparse.Namespace) -> int:
    config = _resolve_config(args)
    config.validate()

    suite_path = args.suite or example_suite_path()
    suite = load_suite(suite_path)
    synthesizer = get_synthesizer(config.synthesizer)
    loop_config = LoopConfig(
        samples=config.samples,
        repair_budget=config.repair_budget,
        timeout=config.timeout,
    )

    reports = [solve_task(task, synthesizer, config=loop_config) for task in suite]
    print(_render(reports, args.format))

    solved = sum(1 for r in reports if r.solved)
    # Non-zero exit if any task went unsolved, so `run` doubles as a gate in CI.
    return 0 if solved == len(reports) else 1


def _render(reports: list, fmt: str) -> str:
    if fmt == "markdown":
        return render_markdown(reports)
    if fmt == "json":
        return "[\n" + ",\n".join(render_json(r, indent=2) for r in reports) + "\n]"
    return "\n".join(render_text(r) for r in reports)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    result: int = args.func(args)
    return result
