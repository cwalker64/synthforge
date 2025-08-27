"""Tests for functional-correctness metrics."""

import pytest

from synthforge.eval.metrics import pass_at_k


def test_pass_at_1_all_correct() -> None:
    assert pass_at_k(10, 10, 1) == 1.0


def test_pass_at_1_none_correct() -> None:
    assert pass_at_k(10, 0, 1) == 0.0


def test_pass_at_1_half_correct() -> None:
    assert pass_at_k(10, 5, 1) == pytest.approx(0.5)


def test_pass_at_k_monotonic_in_k() -> None:
    v1 = pass_at_k(20, 3, 1)
    v5 = pass_at_k(20, 3, 5)
    assert v5 > v1


def test_pass_at_k_when_budget_exceeds_failures() -> None:
    # If there are fewer failures than k, success is guaranteed.
    assert pass_at_k(5, 3, 5) == 1.0


def test_rejects_more_correct_than_samples() -> None:
    with pytest.raises(ValueError):
        pass_at_k(3, 4, 1)
