"""Command-line interface for synthforge.

The full subcommand set (run/eval/repair/report) is wired up incrementally.
This scaffold only supports ``--version``.
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

from synthforge.version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="synthforge", description=__doc__)
    parser.add_argument("--version", action="version", version=f"synthforge {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
