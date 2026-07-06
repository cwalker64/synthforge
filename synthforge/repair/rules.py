"""A repairer that applies :mod:`synthforge.repair.operators` as a search."""

from __future__ import annotations

from collections.abc import Sequence

from synthforge.repair.base import RepairContext
from synthforge.repair.operators import OPERATORS, RepairOperator
from synthforge.types import Candidate


class RuleRepairer:
    """Generate repaired candidates by mutating the failing source.

    Every registered operator is applied to the failing candidate; the distinct
    variants (excluding the original) are returned in operator order, capped at
    ``max_variants`` so a pathological candidate cannot explode the search.
    """

    name = "rule"

    def __init__(
        self,
        operators: Sequence[RepairOperator] | None = None,
        max_variants: int = 32,
    ) -> None:
        self._operators = list(operators) if operators is not None else list(OPERATORS)
        self._max_variants = max_variants

    def repair(self, ctx: RepairContext) -> list[Candidate]:
        original = ctx.candidate.source
        seen = {original}
        repaired: list[Candidate] = []
        for operator in self._operators:
            for variant in operator(original):
                if variant in seen:
                    continue
                seen.add(variant)
                repaired.append(
                    Candidate(
                        variant,
                        origin=self.name,
                        metadata={"operator": operator.__name__},
                    )
                )
                if len(repaired) >= self._max_variants:
                    return repaired
        return repaired
