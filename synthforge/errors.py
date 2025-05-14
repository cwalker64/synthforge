"""Exception hierarchy for synthforge.

All errors raised deliberately by the library derive from :class:`SynthForgeError`
so callers can catch the whole family with a single ``except`` clause.
"""

from __future__ import annotations


class SynthForgeError(Exception):
    """Base class for every error raised by synthforge."""


class TaskError(SynthForgeError):
    """A task specification is malformed or inconsistent."""


class SuiteLoadError(SynthForgeError):
    """A task suite could not be read or parsed."""


class SynthesisError(SynthForgeError):
    """A synthesizer failed to produce candidates."""


class EvaluationError(SynthForgeError):
    """Something went wrong while evaluating a candidate."""


class SandboxTimeout(EvaluationError):
    """A sandboxed candidate exceeded its wall-clock budget."""


class RepairError(SynthForgeError):
    """A repair strategy failed to run."""


class ConfigError(SynthForgeError):
    """A run configuration is invalid."""
