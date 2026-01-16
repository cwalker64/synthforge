"""synthforge: program synthesis and test-based evaluation."""

from synthforge.config import RunConfig
from synthforge.errors import SynthForgeError
from synthforge.eval.runner import evaluate
from synthforge.loop import LoopConfig, solve_task
from synthforge.tasks import TaskSuite, load_suite
from synthforge.types import (
    Candidate,
    EvalResult,
    RepairStep,
    RunReport,
    Task,
    TestOutcome,
)
from synthforge.version import __version__

__all__ = [
    "__version__",
    "Task",
    "Candidate",
    "TestOutcome",
    "EvalResult",
    "RepairStep",
    "RunReport",
    "TaskSuite",
    "load_suite",
    "evaluate",
    "solve_task",
    "LoopConfig",
    "RunConfig",
    "SynthForgeError",
]
