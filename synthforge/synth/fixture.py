"""A synthesizer that replays a fixed bank of candidate programs.

:class:`FixtureSynthesizer` is deterministic and completely offline. It is the
simplest way to drive the evaluation and repair machinery with known inputs -
either hand-written solutions or previously recorded model completions.
Candidates come from an explicit bank keyed by ``task_id``, falling back to a
``candidates`` list on the task's ``hints``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from synthforge.synth.base import AbstractSynthesizer
from synthforge.types import Candidate, Task


class FixtureSynthesizer(AbstractSynthesizer):
    name = "fixture"

    def __init__(self, bank: Mapping[str, Sequence[str]] | None = None) -> None:
        self._bank: dict[str, list[str]] = {key: list(value) for key, value in (bank or {}).items()}

    def add(self, task_id: str, sources: Sequence[str]) -> None:
        """Register (or extend) the candidate list for a task."""
        self._bank.setdefault(task_id, []).extend(sources)

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        sources = self._bank.get(task.task_id)
        if sources is None:
            sources = list(task.hints.get("candidates", []))
        return [Candidate(src, origin=self.name) for src in sources[:n]]
