"""Run configuration.

A :class:`RunConfig` bundles the knobs for a synth/eval/repair run. It can be
built from a plain mapping (e.g. decoded JSON) and converted to the loop's
lighter-weight :class:`~synthforge.loop.LoopConfig`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

from synthforge.errors import ConfigError

_FIELDS = ("synthesizer", "samples", "repair_budget", "timeout", "seed")

PathLike = Union[str, Path]


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


def load_config(path: PathLike) -> RunConfig:
    """Load a :class:`RunConfig` from a JSON file or a simple ``key: value`` file.

    To keep the package dependency-free there is no YAML parser; instead a tiny
    flat ``key: value`` format is accepted as a convenience, and anything that
    parses as JSON is treated as JSON.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _parse_flat(text)
    if not isinstance(data, Mapping):
        raise ConfigError(f"{path}: config must be a mapping")
    return RunConfig.from_mapping(data)


def _parse_flat(text: str) -> dict[str, Any]:
    """Parse a minimal ``key: value`` document (one pair per line)."""
    out: dict[str, Any] = {}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ConfigError(f"line {lineno}: expected 'key: value', got {raw!r}")
        key, _, value = line.partition(":")
        out[key.strip()] = _coerce(value.strip())
    return out


def _coerce(value: str) -> Any:
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return value.strip("'\"")
