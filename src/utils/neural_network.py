"""Shared helpers for the trainable neural network page."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

EPSILON = 1e-9


@dataclass
class NetworkParams:
    """Container for a tiny 2-2-1 neural network."""

    weights_hidden: np.ndarray
    bias_hidden: np.ndarray
    weights_output: np.ndarray
    bias_output: float

    def copy(self) -> NetworkParams:
        return NetworkParams(
            weights_hidden=self.weights_hidden.copy(),
            bias_hidden=self.bias_hidden.copy(),
            weights_output=self.weights_output.copy(),
            bias_output=float(self.bias_output),
        )


def create_network_params(seed: int = 1) -> NetworkParams:
    """Create reproducible initial parameters for the AND demo."""

    rng = np.random.default_rng(seed)
    return NetworkParams(
        weights_hidden=rng.normal(0.0, 0.8, size=(2, 2)),
        bias_hidden=np.zeros(2, dtype=float),
        weights_output=rng.normal(0.0, 0.8, size=2),
        bias_output=0.0,
    )


def params_to_dict(params: NetworkParams) -> dict[str, object]:
    """Convert parameters into a Streamlit-friendly dictionary."""

    return {
        "weights_hidden": params.weights_hidden.copy(),
        "bias_hidden": params.bias_hidden.copy(),
        "weights_output": params.weights_output.copy(),
        "bias_output": float(params.bias_output),
    }


def params_from_dict(data: dict[str, object]) -> NetworkParams:
    """Create a parameter object from a stored snapshot."""

    return NetworkParams(
        weights_hidden=np.asarray(data["weights_hidden"], dtype=float).copy(),
        bias_hidden=np.asarray(data["bias_hidden"], dtype=float).copy(),
        weights_output=np.asarray(data["weights_output"], dtype=float).copy(),
        bias_output=float(data["bias_output"]),
    )


def snapshot_to_params(snapshot: dict[str, object]) -> NetworkParams:
    """Extract parameters from a training-history snapshot."""

    return params_from_dict(snapshot)


def sigmoid(values: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable sigmoid."""

    clipped = np.clip(values, -500, 500)
    return 1.0 / (1.0 + np.exp(-clipped))


def binary_cross_entropy(targets: np.ndarray, predictions: np.ndarray) -> float:
    """Average binary cross-entropy loss."""

    clipped_predictions = np.clip(predictions, EPSILON, 1.0 - EPSILON)
    loss = -(
        targets * np.log(clipped_predictions) + (1.0 - targets) * np.log(1.0 - clipped_predictions)
    )
    return float(np.mean(loss))


def forward_pass(inputs: np.ndarray, params: NetworkParams) -> dict[str, object]:
    """Run a forward pass for one sample or a full batch."""

    batch = np.asarray(inputs, dtype=float)
    single_input = batch.ndim == 1
    if single_input:
        batch = batch[np.newaxis, :]

    hidden_raw = batch @ params.weights_hidden.T + params.bias_hidden
    hidden_activation = sigmoid(hidden_raw)
    output_raw = hidden_activation @ params.weights_output + params.bias_output
    output_activation = sigmoid(output_raw)

    if single_input:
        return {
            "hidden_raw": hidden_raw[0],
            "hidden_activation": hidden_activation[0],
            "output_raw": float(output_raw[0]),
            "output_activation": float(output_activation[0]),
        }

    return {
        "hidden_raw": hidden_raw,
        "hidden_activation": hidden_activation,
        "output_raw": output_raw,
        "output_activation": output_activation,
    }


def evaluate_and_truth_table(params: NetworkParams) -> dict[str, object]:
    """Evaluate the network on the full AND truth table."""

    inputs = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=float)
    targets = np.array([0.0, 0.0, 0.0, 1.0], dtype=float)

    forward = forward_pass(inputs, params)
    probabilities = np.asarray(forward["output_activation"], dtype=float)
    predictions = (probabilities >= 0.5).astype(int)
    accuracy = float(np.mean(predictions == targets))
    loss = binary_cross_entropy(targets, probabilities)

    rows = []
    for (x1, x2), probability, prediction, target in zip(
        inputs,
        probabilities,
        predictions,
        targets,
        strict=False,
    ):
        rows.append(
            {
                "Input 1": int(x1),
                "Input 2": int(x2),
                "Probability": round(float(probability), 4),
                "Prediction": int(prediction),
                "Expected": int(target),
            }
        )

    return {
        "inputs": inputs,
        "targets": targets,
        "probabilities": probabilities,
        "predictions": predictions,
        "accuracy": accuracy,
        "loss": loss,
        "rows": rows,
    }


def train_and_network(
    initial_params: NetworkParams | None = None,
    learning_rate: float = 0.3,
    epochs: int = 300,
    seed: int = 1,
) -> tuple[NetworkParams, list[dict[str, object]]]:
    """Train a 2-2-1 network on the AND truth table with batch gradient descent."""

    inputs = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=float)
    targets = np.array([0.0, 0.0, 0.0, 1.0], dtype=float)
    params = (
        initial_params.copy() if initial_params is not None else create_network_params(seed=seed)
    )
    history: list[dict[str, object]] = []

    def capture_snapshot(epoch: int) -> None:
        evaluation = evaluate_and_truth_table(params)
        snapshot = params_to_dict(params)
        snapshot["epoch"] = epoch
        snapshot["loss"] = evaluation["loss"]
        snapshot["accuracy"] = evaluation["accuracy"]
        history.append(snapshot)

    capture_snapshot(epoch=0)

    for epoch in range(1, epochs + 1):
        forward = forward_pass(inputs, params)
        hidden_activation = np.asarray(forward["hidden_activation"], dtype=float)
        output_activation = np.asarray(forward["output_activation"], dtype=float)

        output_error = output_activation - targets
        sample_count = len(inputs)

        grad_weights_output = hidden_activation.T @ output_error / sample_count
        grad_bias_output = float(np.mean(output_error))

        hidden_error = (
            np.outer(output_error, params.weights_output)
            * hidden_activation
            * (1.0 - hidden_activation)
        )
        grad_weights_hidden = hidden_error.T @ inputs / sample_count
        grad_bias_hidden = hidden_error.mean(axis=0)

        params.weights_output -= learning_rate * grad_weights_output
        params.bias_output -= learning_rate * grad_bias_output
        params.weights_hidden -= learning_rate * grad_weights_hidden
        params.bias_hidden -= learning_rate * grad_bias_hidden

        capture_snapshot(epoch=epoch)

    return params, history
