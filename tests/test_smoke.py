"""Smoke tests that the package imports and exposes a version."""

import synthforge


def test_version_is_a_string() -> None:
    assert isinstance(synthforge.__version__, str)
    assert synthforge.__version__


def test_version_looks_semverish() -> None:
    parts = synthforge.__version__.split(".")
    assert len(parts) >= 2
