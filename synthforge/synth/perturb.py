"""A synthesizer that perturbs a seed solution.

Given a seed program on ``task.hints["seed"]``, this backend emits the seed
plus a spread of single-edit perturbations produced by the repair operators. It
is handy for search-style workflows and for stress-testing the evaluator, and it
shares its mutation library with :mod:`synthforge.repair`.
"""

from __future__ import annotations

from synthforge.repair.operators import OPERATORS
from synthforge.synth.base import AbstractSynthesizer
from synthforge.types import Candidate, Task


class PerturbSynthesizer(AbstractSynthesizer):
    name = "perturb"

    def __init__(self, seed_key: str = "seed") -> None:
        self._seed_key = seed_key

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        seed = task.hints.get(self._seed_key)
        if not isinstance(seed, str) or not seed:
            return []

        candidates = [Candidate(seed, origin=self.name, metadata={"perturbation": "seed"})]
        for operator in OPERATORS:
            for variant in operator(seed):
                candidates.append(
                    Candidate(
                        variant, origin=self.name, metadata={"perturbation": operator.__name__}
                    )
                )
                if len(candidates) >= n:
                    return candidates[:n]
        return candidates[:n]
