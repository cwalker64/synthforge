"""Run configuration.

A :class:`RunConfig` bundles the knobs for a synth/eval/repair run. Loading
from a mapping or file is added later; for now it only holds defaults.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunConfig:
    """Options for a single run over a task suite."""

    synthesizer: str = "template"
    samples: int = 1
    repair_budget: int = 3
    timeout: float = 5.0
    seed: int = 0
