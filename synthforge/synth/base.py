"""The :class:`Synthesizer` protocol."""

from __future__ import annotations

import abc
from typing import Protocol, runtime_checkable

from synthforge.types import Candidate, Task


@runtime_checkable
class Synthesizer(Protocol):
    """Produces candidate programs for a task.

    Implementations must be deterministic given the same ``task`` and ``n`` so
    that evaluation results are reproducible. ``name`` is used in reports and by
    the registry.
    """

    name: str

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        """Return up to ``n`` candidate solutions for ``task``."""
        ...


class AbstractSynthesizer(abc.ABC):
    """Convenience base implementing :class:`Synthesizer`.

    Subclasses set :attr:`name` and implement :meth:`synthesize`. Provided for
    ergonomics only; a plain object with the right attributes also satisfies the
    protocol.
    """

    name: str = "abstract"

    @abc.abstractmethod
    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:  # pragma: no cover
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
