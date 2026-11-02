"""Unit tests for the LEAF CLI."""

from leaf.cli.main import main


def test_cli_version(capsys):
    """Test that leaf --version prints version and exits."""
    try:
        main(["--version"])
    except SystemExit as e:
        assert e.code == 0
    captured = capsys.readouterr()
    assert "leaf 0.1.0" in captured.out or "leaf 0.1.0" in captured.err


def test_cli_help(capsys):
    """Test that leaf without arguments displays help message."""
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()
    assert "validate-config" in captured.out
    assert "info" in captured.out


def test_cli_info(capsys):
    """Test that leaf info runs and outputs environment details."""
    ret = main(["info"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "LEAF Benchmark Framework" in captured.out
    assert "Python Runtime" in captured.out


def test_cli_validate_config_default(capsys):
    """Test that validate-config passes on the default config."""
    ret = main(["validate-config", "config/default_config.yaml"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "SUCCESS" in captured.out
    assert "pilot_baseline" in captured.out


def test_cli_validate_config_missing_file(capsys):
    """Test that validate-config reports failure on a non-existent file."""
    ret = main(["validate-config", "non_existent_config.yaml"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "ERROR" in captured.err

