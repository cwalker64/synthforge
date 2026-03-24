"""Functional-correctness metrics.

The headline metric is ``pass@k``: the probability that at least one of ``k``
samples drawn (without replacement) from ``n`` generated candidates is correct,
given that ``c`` of them are correct. We use the standard unbiased estimator
from Chen et al. (2021), evaluated in a numerically stable product form so it
never allocates the full binomial coefficients.
"""

from __future__ import annotations


def pass_at_k(num_samples: int, num_correct: int, k: int) -> float:
    """Unbiased estimate of pass@k.

    Args:
        num_samples: total candidates generated for the task (``n``).
        num_correct: how many of them passed all tests (``c``).
        k: the sampling budget.
    """
    n, c = num_samples, num_correct
    if n < 0 or c < 0:
        raise ValueError("num_samples and num_correct must be non-negative")
    if c > n:
        raise ValueError("num_correct cannot exceed num_samples")
    if k < 1:
        raise ValueError("k must be >= 1")
    if k > n:
        # Sampling more than we generated is undefined for the estimator; the
        # best honest answer is the observed proportion of correct samples.
        return 1.0 if c == n else c / n if n else 0.0
    if n - c < k:
        return 1.0
    prod = 1.0
    for i in range(n - c + 1, n + 1):
        prod *= 1.0 - k / i
    return 1.0 - prod
