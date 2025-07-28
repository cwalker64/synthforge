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
import os


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
        try:
            setattr(module, attr, None)
        except (AttributeError, TypeError):  # pragma: no cover
            pass


def _disable_module(module_name: str, attrs: tuple[str, ...]) -> None:
    try:
        module = __import__(module_name)
    except ImportError:  # pragma: no cover
        return
    for attr in attrs:
        _disable(module, attr)
