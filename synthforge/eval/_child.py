"""Child process that executes a candidate against test snippets.

This module is spawned as ``python -m synthforge.eval._child`` by
:mod:`synthforge.eval.sandbox`. It reads a JSON payload from stdin, executes
the candidate program in a hardened namespace, runs each test snippet in a
fresh copy of that namespace, and writes a JSON result document to stdout.

Keeping this logic in its own lightweight module means the subprocess starts
without importing the rest of the package.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import time
from typing import Any

from synthforge.eval.sandbox import reliability_guard


def _run(payload: dict[str, Any]) -> dict[str, Any]:
    source: str = payload.get("source", "")
    setup: str = payload.get("setup", "")
    tests: list[str] = list(payload.get("tests", []))

    reliability_guard()

    program = f"{setup}\n{source}" if setup else source
    namespace: dict[str, Any] = {"__name__": "__candidate__"}

    try:
        compiled = compile(program, "<candidate>", "exec")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exec(compiled, namespace)  # noqa: S102 - sandboxed on purpose
    except BaseException as exc:  # noqa: BLE001 - report any failure to the parent
        error = f"{type(exc).__name__}: {exc}"
        return {"outcomes": [_fail(i, error) for i in range(len(tests))]}

    outcomes = [_run_test(i, test, namespace) for i, test in enumerate(tests)]
    return {"outcomes": outcomes}


def _run_test(index: int, test: str, base_ns: dict[str, Any]) -> dict[str, Any]:
    local_ns = dict(base_ns)
    start = time.perf_counter()
    try:
        compiled = compile(test, f"<test-{index}>", "exec")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exec(compiled, local_ns)  # noqa: S102 - sandboxed on purpose
    except BaseException as exc:  # noqa: BLE001
        return {
            "index": index,
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
            "duration": time.perf_counter() - start,
        }
    return {"index": index, "passed": True, "error": None, "duration": time.perf_counter() - start}


def _fail(index: int, error: str) -> dict[str, Any]:
    return {"index": index, "passed": False, "error": error, "duration": 0.0}


def main() -> int:
    payload = json.loads(sys.stdin.read())
    result = _run(payload)
    # Write at the file-descriptor level so candidate code that rebinds
    # ``sys.stdout`` cannot corrupt the result document.
    os.write(1, json.dumps(result).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
