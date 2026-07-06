"""Tests for AST repair operators."""

from synthforge.repair.operators import (
    flip_comparisons,
    swap_binary_operators,
    tweak_int_constants,
)


def test_swap_binary_operators_reaches_correct_form() -> None:
    buggy = "def add(a, b):\n    return a - b\n"
    variants = swap_binary_operators(buggy)
    assert any("a + b" in v for v in variants)


def test_flip_comparisons_offers_alternatives() -> None:
    buggy = "def is_pos(x):\n    return x < 0\n"
    variants = flip_comparisons(buggy)
    assert any(">" in v for v in variants)


def test_tweak_int_constants_covers_both_directions() -> None:
    buggy = "def f(n):\n    return n + 1\n"
    variants = tweak_int_constants(buggy)
    assert any("n + 2" in v for v in variants)
    assert any("n + 0" in v for v in variants)


def test_operators_tolerate_syntax_errors() -> None:
    assert swap_binary_operators("def broken(:\n") == []
    assert flip_comparisons("def broken(:\n") == []
    assert tweak_int_constants("def broken(:\n") == []
