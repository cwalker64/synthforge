"""Subprocess sandbox for running untrusted candidate code.

Evaluation happens in a separate Python process so a misbehaving candidate
cannot corrupt the evaluator. Two layers of defence are applied:

* **process isolation** - the candidate runs in a child process with a hard
  wall-clock timeout enforced by the parent (see :func:`run_in_sandbox`);
* **reliability guard** - inside the child, obviously destructive calls
  (filesystem removal, process spawning, ``os.system`` ...) are disabled
  before any candidate code runs (see :func:`reliability_guard`).

This is defence in depth for accidental damage, not a security boundary for
adversarial code. Run genuinely untrusted models inside a container or VM.
"""

from __future__ import annotations

import builtins
import contextlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SandboxOutcome:
    """Raw result of one sandboxed run, before mapping to domain types."""

    outcomes: list[dict[str, Any]] = field(default_factory=list)
    timed_out: bool = False
    duration: float = 0.0
    error: str | None = None


def run_in_sandbox(
    source: str,
    tests: list[str],
    *,
    setup: str = "",
    timeout: float = 5.0,
) -> SandboxOutcome:
    """Execute ``source`` against ``tests`` in a child process.

    The child is given ``timeout`` seconds of wall-clock time. If it overruns,
    it is terminated and every test is reported as failed with ``timed_out``.
    """
    payload = json.dumps({"source": source, "setup": setup, "tests": tests})
    cmd = [sys.executable, "-m", "synthforge.eval._child"]
    start = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(payload, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return SandboxOutcome(
            outcomes=[_timeout_outcome(i) for i in range(len(tests))],
            timed_out=True,
            duration=time.perf_counter() - start,
        )

    duration = time.perf_counter() - start
    if not out.strip():
        detail = err.strip().splitlines()[-1] if err.strip() else "no output from sandbox"
        return SandboxOutcome(
            outcomes=[_error_outcome(i, detail) for i in range(len(tests))],
            duration=duration,
            error=detail,
        )
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        return SandboxOutcome(
            outcomes=[_error_outcome(i, "malformed sandbox output") for i in range(len(tests))],
            duration=duration,
            error="malformed sandbox output",
        )
    return SandboxOutcome(outcomes=list(parsed.get("outcomes", [])), duration=duration)


def _timeout_outcome(index: int) -> dict[str, Any]:
    return {"index": index, "passed": False, "error": "timed out", "duration": 0.0}


def _error_outcome(index: int, detail: str) -> dict[str, Any]:
    return {"index": index, "passed": False, "error": detail, "duration": 0.0}


def reliability_guard(max_memory_bytes: int | None = None) -> None:
    """Disable a set of destructive operations in the current process.

    Intended to be called once at the top of the sandbox child, before any
    candidate code executes. Adapted from the guard used by common code-eval
    harnesses, trimmed to the calls that matter for offline evaluation.
    """
    if max_memory_bytes is not None:
        _limit_memory(max_memory_bytes)

    os.environ["OMP_NUM_THREADS"] = "1"

    # Filesystem mutation.
    for name in ("remove", "removedirs", "rmdir", "unlink", "rename", "renames", "truncate"):
        _disable(os, name)
    _disable_module("shutil", ("rmtree", "move", "chown"))

    # Process / shell execution.
    for name in ("system", "kill", "fork", "abort", "killpg"):
        _disable(os, name)
    _disable_module("subprocess", ("Popen", "call", "run", "check_output"))

    # Interpreter shutdown shortcuts.
    for name in ("exit", "quit"):
        if hasattr(builtins, name):
            setattr(builtins, name, None)


def _limit_memory(max_bytes: int) -> None:
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
    except (ImportError, ValueError, OSError):  # pragma: no cover - platform dependent
        pass


def _disable(module: object, attr: str) -> None:
    if hasattr(module, attr):
        with contextlib.suppress(AttributeError, TypeError):  # pragma: no cover
            setattr(module, attr, None)


def _disable_module(module_name: str, attrs: tuple[str, ...]) -> None:
    try:
        module = __import__(module_name)
    except ImportError:  # pragma: no cover
        return
    for attr in attrs:
        _disable(module, attr)
