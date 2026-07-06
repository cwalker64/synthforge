"""Tests for run configuration loading."""

import pytest

from synthforge.config import RunConfig, load_config
from synthforge.errors import ConfigError


def test_defaults() -> None:
    cfg = RunConfig()
    assert cfg.synthesizer == "template"
    assert cfg.samples == 1


def test_from_mapping_overrides() -> None:
    cfg = RunConfig.from_mapping({"synthesizer": "fixture", "samples": 4})
    assert cfg.synthesizer == "fixture"
    assert cfg.samples == 4


def test_from_mapping_rejects_unknown_keys() -> None:
    with pytest.raises(ConfigError):
        RunConfig.from_mapping({"nope": 1})


def test_validate_catches_bad_values() -> None:
    with pytest.raises(ConfigError):
        RunConfig(samples=0).validate()


def test_load_json_config(tmp_path) -> None:
    path = tmp_path / "cfg.json"
    path.write_text('{"samples": 3, "timeout": 2.5}', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.samples == 3
    assert cfg.timeout == 2.5


def test_load_flat_config(tmp_path) -> None:
    path = tmp_path / "cfg.txt"
    path.write_text("synthesizer: fixture\nsamples: 2\n# a comment\n", encoding="utf-8")
    cfg = load_config(path)
    assert cfg.synthesizer == "fixture"
    assert cfg.samples == 2
