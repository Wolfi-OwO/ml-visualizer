"""Tests for the trainable neural network helpers."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.neural_network import (  # noqa: E402
    create_network_params,
    evaluate_and_truth_table,
    forward_pass,
    train_and_network,
)


class TestNeuralNetworkUtils:
    """Validate the shared neural-network helper functions."""

    def test_forward_pass_batch_shapes(self):
        """Forward pass should return sensible batch dimensions."""

        params = create_network_params(seed=1)
        batch = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=float)

        result = forward_pass(batch, params)

        assert result["hidden_activation"].shape == (2, 2)
        assert result["output_activation"].shape == (2,)

    def test_forward_pass_single_sample_returns_scalar(self):
        """Single-sample inference should expose scalar output values."""

        params = create_network_params(seed=1)
        result = forward_pass(np.array([1.0, 1.0]), params)

        assert isinstance(result["output_raw"], float)
        assert isinstance(result["output_activation"], float)

    def test_train_and_network_learns_and_gate(self):
        """Training should converge on the full AND truth table."""

        trained_params, history = train_and_network(learning_rate=0.3, epochs=300, seed=1)
        evaluation = evaluate_and_truth_table(trained_params)

        assert evaluation["predictions"].tolist() == [0, 0, 0, 1]
        assert evaluation["accuracy"] == 1.0
        assert history[-1]["loss"] < history[0]["loss"]
