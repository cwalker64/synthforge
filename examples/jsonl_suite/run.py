"""Run the CLI over a small external JSONL suite.

Equivalent to:  synthforge run examples/jsonl_suite/suite.jsonl
"""

from pathlib import Path

from synthforge.cli import main

SUITE = Path(__file__).with_name("suite.jsonl")

if __name__ == "__main__":
    raise SystemExit(main(["run", str(SUITE), "--format", "markdown"]))
