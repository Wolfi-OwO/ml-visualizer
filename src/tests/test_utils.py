"""Unit tests for utils.config and utils.health."""

import pathlib
import sys

# Ensure `src` is on sys.path so we can import `utils` package
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from utils.config import (
    get_config,
    get_environment,
    get_log_level,
    get_max_concurrent_users,
    get_version,
    is_debug_enabled,
)
from utils.health import get_health_status, is_healthy


def test_get_version_prefers_env(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "2.3.4")
    assert get_version() == "2.3.4"
    monkeypatch.delenv("APP_VERSION", raising=False)


def test_get_version_reads_file_when_no_env(monkeypatch, tmp_path):
    # Ensure APP_VERSION not set and create a VERSION file in cwd
    monkeypatch.delenv("APP_VERSION", raising=False)
    ver_file = tmp_path / "VERSION"
    ver_file.write_text("5.5.5\n")
    monkeypatch.chdir(tmp_path)

    assert get_version() == "5.5.5"


def test_get_config_and_environment_and_log_level(monkeypatch):
    monkeypatch.delenv("SOME_KEY", raising=False)
    assert get_config("SOME_KEY", "default") == "default"

    monkeypatch.setenv("ENVIRONMENT_NAME", "testing")
    assert get_environment() == "testing"

    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert get_log_level() == "DEBUG"


def test_is_debug_enabled_and_max_users(monkeypatch):
    monkeypatch.setenv("ENABLE_DEBUG_MODE", "true")
    assert is_debug_enabled() is True

    monkeypatch.setenv("ENABLE_DEBUG_MODE", "false")
    assert is_debug_enabled() is False

    monkeypatch.setenv("MAX_CONCURRENT_USERS", "42")
    assert get_max_concurrent_users() == 42


def test_health_status_and_is_healthy(monkeypatch, tmp_path):
    # Create a minimal project layout: VERSION file and pages directory
    (tmp_path / "VERSION").write_text("0.0.1")
    (tmp_path / "pages").mkdir()
    monkeypatch.chdir(tmp_path)

    status = get_health_status()
    assert status["status"] == "healthy"
    assert isinstance(status["timestamp"], str)
    assert status["checks"]["version_file"] is True
    assert status["checks"]["pages_directory"] is True
    assert is_healthy() is True


def test_is_healthy_false_when_checks_fail(monkeypatch, tmp_path):
    # Empty temp dir => no VERSION and no pages
    monkeypatch.chdir(tmp_path)
    assert is_healthy() is False
