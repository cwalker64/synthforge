"""Tests for the synthesizer registry."""

import pytest

from synthforge.errors import ConfigError
from synthforge.synth.registry import available, get_synthesizer, register
from synthforge.synth.template import TemplateSynthesizer


def test_builtin_backends_registered() -> None:
    names = available()
    assert "template" in names
    assert "fixture" in names


def test_get_synthesizer_returns_instance() -> None:
    synth = get_synthesizer("template")
    assert isinstance(synth, TemplateSynthesizer)


def test_unknown_name_raises() -> None:
    with pytest.raises(ConfigError):
        get_synthesizer("does-not-exist")


def test_register_custom_backend() -> None:
    register("template-copy", TemplateSynthesizer)
    assert "template-copy" in available()
