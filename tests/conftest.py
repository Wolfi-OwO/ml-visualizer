"""
Test configuration for DSAI-5BHIF ML Visualizer

This module contains pytest configuration and shared fixtures.
"""

import os
import sys

import numpy as np
import pytest

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ============================================
# FIXTURES
# ============================================


@pytest.fixture
def sample_and_data():
    """Provide AND gate training data."""
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 0, 0, 1])
    return X, y


@pytest.fixture
def sample_knn_points():
    """Provide sample points for KNN testing."""
    return [
        (0.1, 0.1, "A"),
        (0.2, 0.1, "A"),
        (0.1, 0.2, "A"),
        (0.8, 0.8, "B"),
        (0.9, 0.9, "B"),
    ]


@pytest.fixture
def perceptron_weights():
    """Provide trained perceptron weights for AND gate."""
    return {
        "weights": np.array([1.5, 1.5]),
        "bias": -2.0,
        "learning_rate": 0.3,
    }


@pytest.fixture
def neural_network_weights():
    """Provide neural network weights for AND gate."""
    return {
        "weights_hidden": np.array([[20.0, 20.0], [20.0, 20.0]]),
        "bias_hidden": np.array([-30.0, -30.0]),
        "weights_output": np.array([20.0, 20.0]),
        "bias_output": -10.0,
    }


@pytest.fixture
def gradient_descent_config():
    """Provide gradient descent configuration."""
    return {
        "x_start": 8.0,
        "learning_rate": 0.1,
        "iterations": 50,
    }


# ============================================
# HELPER FUNCTIONS AS FIXTURES
# ============================================


@pytest.fixture
def sigmoid():
    """Provide sigmoid activation function."""

    def _sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    return _sigmoid


@pytest.fixture
def euclidean_distance():
    """Provide Euclidean distance function."""

    def _distance(p1, p2):
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2, strict=False)))

    return _distance


# ============================================
# PYTEST CONFIGURATION
# ============================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to all tests in test_algorithms.py
        if "test_algorithms" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in test_pages.py
        if "test_pages" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
