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


def _parse(source: str) -> ast.Module | None:
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def _unparse(tree: ast.Module) -> str:
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def swap_binary_operators(source: str) -> list[str]:
    """Try replacing each arithmetic operator with a related one."""
    tree = _parse(source)
    if tree is None:
        return []
    count = len(_binops(tree))
    variants: list[str] = []
    for idx in range(count):
        node = _binops(tree)[idx]
        for alt in _BINOP_ALTS[type(node.op)]:
            clone = copy.deepcopy(tree)
            _binops(clone)[idx].op = alt()
            variants.append(_unparse(clone))
    return variants


def flip_comparisons(source: str) -> list[str]:
    """Try replacing each single comparison operator with a related one."""
    tree = _parse(source)
    if tree is None:
        return []
    count = len(_compares(tree))
    variants: list[str] = []
    for idx in range(count):
        node = _compares(tree)[idx]
        for alt in _CMP_ALTS[type(node.ops[0])]:
            clone = copy.deepcopy(tree)
            _compares(clone)[idx].ops[0] = alt()
            variants.append(_unparse(clone))
    return variants


def tweak_int_constants(source: str) -> list[str]:
    """Try nudging each integer literal by plus or minus one (off-by-one fixes)."""
    tree = _parse(source)
    if tree is None:
        return []
    count = len(_int_constants(tree))
    variants: list[str] = []
    for idx in range(count):
        for delta in (1, -1):
            clone = copy.deepcopy(tree)
            target = _int_constants(clone)[idx]
            current = target.value
            if isinstance(current, int):
                target.value = current + delta
                variants.append(_unparse(clone))
    return variants


def _binops(tree: ast.AST) -> list[ast.BinOp]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and type(n.op) in _BINOP_ALTS]


def _compares(tree: ast.AST) -> list[ast.Compare]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Compare) and len(n.ops) == 1 and type(n.ops[0]) in _CMP_ALTS
    ]


def _int_constants(tree: ast.AST) -> list[ast.Constant]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, int)
        and not isinstance(n.value, bool)
    ]


OPERATORS: list[RepairOperator] = [
    swap_binary_operators,
    flip_comparisons,
    tweak_int_constants,
]
