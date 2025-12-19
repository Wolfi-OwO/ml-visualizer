"""Health check utilities for the DSAI Webapp application."""

import os
import sys
from datetime import datetime
from typing import Any

from .config import get_environment, get_version


def get_health_status() -> dict[str, Any]:
    """
    Get comprehensive health status of the application.

    Returns:
        Dict containing health check information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": get_version(),
        "environment": get_environment(),
        "python_version": sys.version,
        "checks": {
            "version_file": os.path.exists("VERSION"),
            "pages_directory": os.path.exists("pages") or os.path.exists("src/pages"),
        },
    }


def is_healthy() -> bool:
    """
    Quick health check.

    Returns:
        bool: True if application is healthy
    """
    try:
        status = get_health_status()
        return status["status"] == "healthy" and all(status["checks"].values())
    except Exception:
        return False
