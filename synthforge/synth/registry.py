"""A small registry mapping synthesizer names to factories.

The CLI and :class:`~synthforge.config.RunConfig` refer to synthesizers by
name; this module resolves those names to instances and lets third-party code
register its own backends.
"""

from __future__ import annotations

from typing import Callable

from synthforge.errors import ConfigError
from synthforge.synth.base import Synthesizer
from synthforge.synth.fixture import FixtureSynthesizer
from synthforge.synth.template import TemplateSynthesizer

_FACTORIES: dict[str, Callable[..., Synthesizer]] = {}


def register(name: str, factory: Callable[..., Synthesizer]) -> None:
    """Register ``factory`` under ``name`` (overwrites any existing entry)."""
    _FACTORIES[name] = factory


def get_synthesizer(name: str, **kwargs: object) -> Synthesizer:
    """Instantiate the synthesizer registered under ``name``."""
    try:
        factory = _FACTORIES[name]
    except KeyError:
        known = ", ".join(available()) or "(none)"
        raise ConfigError(f"unknown synthesizer {name!r}; known: {known}") from None
    return factory(**kwargs)


def available() -> list[str]:
    """Return the sorted list of registered synthesizer names."""
    return sorted(_FACTORIES)


register("template", TemplateSynthesizer)
register("fixture", FixtureSynthesizer)
