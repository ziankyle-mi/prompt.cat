"""Tests for promptcat CLI commands."""

from pathlib import Path
from typer.testing import CliRunner
from promptcat.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "promptcat v" in result.output


def test_cli_basic_improve(tmp_path: Path):
    result = runner.invoke(app, ["make a login page using react", "--no-copy"])
    assert result.exit_code == 0
    assert "[OK] Text cleaned" in result.output
    assert "<role>" in result.output
    assert "<task>" in result.output


def test_cli_clean_only():
    result = runner.invoke(app, ["dont   use    a database", "--clean-only"])
    assert result.exit_code == 0
    assert "[OK] Text cleaned" in result.output
    assert "Don't use a database." in result.output


def test_cli_clean_only_raw():
    result = runner.invoke(app, ["dont   use    a database", "--clean-only", "--raw"])
    assert result.exit_code == 0
    assert result.output.strip() == "Don't use a database."


def test_cli_detect_only():
    result = runner.invoke(app, ["build a jwt login api with postgres", "--detect-only"])
    assert result.exit_code == 0
    assert "Authentication detected" in result.output
    assert "Database detected" in result.output
    assert "API detected" in result.output


def test_cli_file_input_and_output(tmp_path: Path):
    in_file = tmp_path / "input.txt"
    out_file = tmp_path / "output.txt"
    in_file.write_text("build a rest api using fastapi", encoding="utf-8")

    result = runner.invoke(app, ["--file", str(in_file), "--output", str(out_file), "--no-copy"])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<role>" in content
    assert "FastAPI" in content


def test_cli_invalid_mode():
    result = runner.invoke(app, ["hello", "--mode", "nonexistent", "--no-copy"])
    assert result.exit_code != 0
