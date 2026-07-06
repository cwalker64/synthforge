"""AST-level repair operators.

Each operator takes a candidate's source and returns a list of *variant*
sources, each differing from the input by a single, targeted mutation. The
repair loop re-evaluates the variants and keeps any that improve the pass rate,
so these operators act as a small, deterministic search neighbourhood rather
than a model that "understands" the bug.

All operators are total: on a syntax error or unsupported construct they return
an empty list instead of raising.
"""

from __future__ import annotations

import ast
import copy
from typing import Callable

RepairOperator = Callable[[str], list[str]]

_BINOP_ALTS: dict[type[ast.operator], tuple[type[ast.operator], ...]] = {
    ast.Add: (ast.Sub, ast.Mult),
    ast.Sub: (ast.Add, ast.Mult),
    ast.Mult: (ast.Add, ast.Sub),
    ast.Div: (ast.FloorDiv,),
    ast.FloorDiv: (ast.Div,),
    ast.Mod: (ast.Mult,),
}

_CMP_ALTS: dict[type[ast.cmpop], tuple[type[ast.cmpop], ...]] = {
    ast.Lt: (ast.LtE, ast.Gt),
    ast.LtE: (ast.Lt, ast.GtE),
    ast.Gt: (ast.GtE, ast.Lt),
    ast.GtE: (ast.Gt, ast.LtE),
    ast.Eq: (ast.NotEq,),
    ast.NotEq: (ast.Eq,),
}


def _eligible(tree: ast.AST, predicate: Callable[[ast.AST], bool]) -> list[ast.AST]:
    return [node for node in ast.walk(tree) if predicate(node)]


def _emit(base: ast.AST, index: int, predicate: Callable[[ast.AST], bool],
          mutate: Callable[[ast.AST], None]) -> str:
    tree = copy.deepcopy(base)
    node = _eligible(tree, predicate)[index]
    mutate(node)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def swap_binary_operators(source: str) -> list[str]:
    """Try replacing each arithmetic operator with a related one."""
    try:
        base = ast.parse(source)
    except SyntaxError:
        return []
    pred = lambda n: isinstance(n, ast.BinOp) and type(n.op) in _BINOP_ALTS  # noqa: E731
    variants: list[str] = []
    for idx, node in enumerate(_eligible(base, pred)):
        for alt in _BINOP_ALTS[type(node.op)]:  # type: ignore[index]
            variants.append(_emit(base, idx, pred, lambda n, a=alt: setattr(n, "op", a())))
    return variants


def flip_comparisons(source: str) -> list[str]:
    """Try replacing each single comparison operator with a related one."""
    try:
        base = ast.parse(source)
    except SyntaxError:
        return []
    pred = lambda n: (  # noqa: E731
        isinstance(n, ast.Compare) and len(n.ops) == 1 and type(n.ops[0]) in _CMP_ALTS
    )
    variants: list[str] = []
    for idx, node in enumerate(_eligible(base, pred)):
        for alt in _CMP_ALTS[type(node.ops[0])]:  # type: ignore[index]
            variants.append(
                _emit(base, idx, pred, lambda n, a=alt: n.ops.__setitem__(0, a()))
            )
    return variants


def tweak_int_constants(source: str) -> list[str]:
    """Try nudging each integer literal by plus or minus one (off-by-one fixes)."""
    try:
        base = ast.parse(source)
    except SyntaxError:
        return []
    pred = lambda n: (  # noqa: E731
        isinstance(n, ast.Constant) and isinstance(n.value, int) and not isinstance(n.value, bool)
    )
    variants: list[str] = []
    for idx, _ in enumerate(_eligible(base, pred)):
        for delta in (1, -1):
            variants.append(
                _emit(base, idx, pred, lambda n, d=delta: setattr(n, "value", n.value + d))
            )
    return variants


OPERATORS: list[RepairOperator] = [
    swap_binary_operators,
    flip_comparisons,
    tweak_int_constants,
]
