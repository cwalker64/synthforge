"""Run configuration.

A :class:`RunConfig` bundles the knobs for a synth/eval/repair run. It can be
built from a plain mapping (e.g. decoded JSON) and converted to the loop's
lighter-weight :class:`~synthforge.loop.LoopConfig`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from synthforge.errors import ConfigError

_FIELDS = ("synthesizer", "samples", "repair_budget", "timeout", "seed")


@dataclass
class RunConfig:
    """Options for a single run over a task suite."""

    synthesizer: str = "template"
    samples: int = 1
    repair_budget: int = 3
    timeout: float = 5.0
    seed: int = 0

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> RunConfig:
        """Build a config from a mapping, rejecting unknown keys."""
        unknown = set(data) - set(_FIELDS)
        if unknown:
            raise ConfigError(f"unknown config keys: {', '.join(sorted(unknown))}")
        try:
            return cls(
                synthesizer=str(data.get("synthesizer", "template")),
                samples=int(data.get("samples", 1)),
                repair_budget=int(data.get("repair_budget", 3)),
                timeout=float(data.get("timeout", 5.0)),
                seed=int(data.get("seed", 0)),
            )
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"invalid config value: {exc}") from exc

    def validate(self) -> None:
        if self.samples < 1:
            raise ConfigError("samples must be >= 1")
        if self.repair_budget < 0:
            raise ConfigError("repair_budget must be >= 0")
        if self.timeout <= 0:
            raise ConfigError("timeout must be positive")

