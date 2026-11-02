"""Unit tests for configuration loading and validation."""

from pathlib import Path

import pytest

from leaf.core.config import load_config, validate_config_dict, validate_config_file
from leaf.core.exceptions import ConfigError


def test_load_default_config():
    """Verify that the shipped default configuration loads and satisfies constraints."""
    config_path = Path("config/default_config.yaml")
    assert config_path.is_file(), "Default configuration file must exist"

    cfg = load_config(config_path)
    assert cfg.experiment.name == "pilot_baseline"
    assert cfg.experiment.repetitions >= 1
    assert cfg.experiment.dry_run is True
    assert cfg.experiment.allow_cloud_calls is False
    assert cfg.sandbox.mode in ("process", "container")
    assert cfg.sandbox.memory_limit_mb >= 32
    assert cfg.budgets.timeout_execution_seconds > 0
    assert "python" in cfg.supported_languages


def test_load_missing_config():
    """Verify that loading a non-existent configuration raises ConfigError."""
    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config("does_not_exist.yaml")


def test_validate_config_dict_invalid_repetitions():
    """Verify that invalid repetition numbers are caught."""
    errors = validate_config_dict({"experiment": {"repetitions": 0}})
    assert any("repetitions" in err for err in errors)


def test_validate_config_dict_invalid_sandbox_mode():
    """Verify that invalid sandbox mode values are rejected."""
    errors = validate_config_dict({"sandbox": {"mode": "unrestricted"}})
    assert any("sandbox.mode" in err for err in errors)


def test_validate_config_dict_invalid_timeouts():
    """Verify that negative or non-numeric timeouts are caught."""
    errors = validate_config_dict({"budgets": {"timeout_execution_seconds": -5.0}})
    assert any("timeout_execution_seconds" in err for err in errors)


def test_validate_config_dict_empty_languages():
    """Verify that empty supported_languages is rejected."""
    errors = validate_config_dict({"supported_languages": []})
    assert any("supported_languages" in err for err in errors)


def test_validate_config_file_syntax_error(tmp_path):
    """Verify that malformed YAML files are flagged cleanly without crash."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("experiment: [invalid yaml: {", encoding="utf-8")

    is_valid, errors = validate_config_file(bad_yaml)
    assert is_valid is False
    assert any("YAML syntax error" in err for err in errors)
