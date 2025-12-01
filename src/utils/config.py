"""Configuration management for the ML Visualizer application."""

import os
from pathlib import Path
from typing import Any


def get_version() -> str:
    """
    Read application version from VERSION file.

    Returns:
        str: Application version string
    """
    try:
        # Check multiple locations for VERSION file
        possible_paths = [
            Path("VERSION"),
            Path("../VERSION"),
            Path(__file__).parent.parent.parent / "VERSION",
        ]

        for version_path in possible_paths:
            if version_path.exists():
                return version_path.read_text().strip()

        return "1.0.0"  # Default fallback
    except Exception:
        return "1.0.0"  # Error fallback


def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration value from environment variables.

    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found

    Returns:
        Configuration value or default
    """
    return os.getenv(key, default)


def get_environment() -> str:
    """
    Get current environment name.

    Returns:
        str: Environment name (testing, staging, or production)
    """
    return get_config("ENVIRONMENT_NAME", "development")


def is_debug_enabled() -> bool:
    """
    Check if debug mode is enabled.

    Returns:
        bool: True if debug mode is enabled
    """
    return get_config("ENABLE_DEBUG_MODE", "false").lower() == "true"


def get_log_level() -> str:
    """
    Get configured log level.

    Returns:
        str: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    return get_config("LOG_LEVEL", "INFO")


def get_max_concurrent_users() -> int:
    """
    Get maximum concurrent users configuration.

    Returns:
        int: Maximum number of concurrent users
    """
    return int(get_config("MAX_CONCURRENT_USERS", "100"))
