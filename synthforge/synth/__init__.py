"""Synthesizers: turn a task prompt into candidate programs.

A synthesizer is any object implementing :class:`Synthesizer`. The reference
backends in this package are deterministic and offline, so the whole pipeline
runs without network access or model weights.
"""

from synthforge.synth.base import Synthesizer

__all__ = ["Synthesizer"]
