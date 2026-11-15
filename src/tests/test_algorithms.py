"""
Test algorithm implementations

This module tests the mathematical algorithms used in the visualizations.
Tests cover: Perceptron, KNN, and Gradient Descent algorithms.
"""

import os
import sys

import numpy as np
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# =============================================================================
# GRADIENT DESCENT TESTS
# =============================================================================


class TestGradientDescent:
    """Test gradient descent algorithm implementation."""

    def test_gradient_descent_function(self):
        """Test the mathematical function f(x) = 0.5 * x^2."""

        def f(x):
            return 0.5 * x**2

        # Test known values
        assert f(0) == 0, "f(0) should equal 0"
        assert f(2) == 2, "f(2) should equal 2"
        assert f(-2) == 2, "f(-2) should equal 2"

    def test_gradient_descent_derivative(self):
        """Test the derivative f'(x) = x."""

        def df(x):
            return x

        # Test known values
        assert df(0) == 0, "df(0) should equal 0"
        assert df(5) == 5, "df(5) should equal 5"
        assert df(-3) == -3, "df(-3) should equal -3"

    def test_gradient_descent_convergence(self):
        """Test that gradient descent converges to minimum."""

        def f(x):
            return 0.5 * x**2

        def df(x):
            return x

        # Start from x=8, learning rate=0.1
        x = 8.0
        lr = 0.1

        # Run 50 iterations for better convergence
        for _ in range(50):
            grad = df(x)
            x = x - lr * grad

        # Should converge reasonably close to 0 (allow for learning rate effects)
        assert abs(x) < 1.0, f"Gradient descent should converge reasonably close to 0, got {x}"

    def test_gradient_descent_loss_decreases(self):
        """Test that loss decreases monotonically during gradient descent."""

        def f(x):
            return 0.5 * x**2

        def df(x):
            return x

        x = 10.0
        lr = 0.1
        losses = [f(x)]

        for _ in range(20):
            grad = df(x)
            x = x - lr * grad
            losses.append(f(x))

        # Each loss should be less than or equal to the previous
        for i in range(1, len(losses)):
            assert losses[i] <= losses[i - 1], (
                f"Loss should decrease: {losses[i - 1]} -> {losses[i]}"
            )

    def test_gradient_descent_step_calculation(self):
        """Test individual gradient descent step calculation."""

        def df(x):
            return x

        x = 8.0
        lr = 0.1

        # Single step: x_new = x - lr * grad
        grad = df(x)
        x_new = x - lr * grad

        # Expected: 8.0 - 0.1 * 8.0 = 8.0 - 0.8 = 7.2
        assert x_new == pytest.approx(7.2), f"Expected 7.2, got {x_new}"

    def test_gradient_descent_different_learning_rates(self):
        """Test gradient descent behavior with different learning rates."""

        def f(x):
            return 0.5 * x**2

        def df(x):
            return x

        x_start = 10.0

        # Small learning rate - slower convergence
        x_small = x_start
        for _ in range(10):
            x_small = x_small - 0.01 * df(x_small)

        # Large learning rate - faster convergence
        x_large = x_start
        for _ in range(10):
            x_large = x_large - 0.3 * df(x_large)

        # Larger lr should converge faster (closer to 0)
        assert abs(x_large) < abs(x_small), "Larger learning rate should converge faster"

    def test_gradient_explosion_detection(self):
        """Test that gradient explosion is detected (as in the app)."""

        def df(x):
            return x

        x = 100.0
        lr = 2.1  # lr > 2 causes divergence for f(x)=0.5x^2 since x_new = x*(1-lr)

        explosion_detected = False
        for _ in range(100):  # More iterations to ensure explosion
            grad = df(x)
            x_new = x - lr * grad
            if abs(x_new) > 1e6:
                explosion_detected = True
                break
            x = x_new

        assert explosion_detected, f"Should detect gradient explosion with lr=2.1, final x={x}"

    def test_gradient_descent_negative_start(self):
        """Test gradient descent starting from negative value."""

        def f(x):
            return 0.5 * x**2

        def df(x):
            return x

        x = -8.0
        lr = 0.1

        for _ in range(50):
            grad = df(x)
            x = x - lr * grad

        # Should still converge to 0 from negative start
        assert abs(x) < 1.0, f"Should converge from negative start, got {x}"


# =============================================================================
# PERCEPTRON TESTS
# =============================================================================


class TestPerceptron:
    """Test perceptron algorithm implementation."""

    def test_perceptron_and_training_data(self):
        """Test that AND training data is correctly defined."""
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([0, 0, 0, 1])

        assert X.shape == (4, 2), "Input data should have shape (4, 2)"
        assert y.shape == (4,), "Output data should have shape (4,)"

        # Test AND logic
        expected_results = [
            (0, 0, 0),  # 0 AND 0 = 0
            (0, 1, 0),  # 0 AND 1 = 0
            (1, 0, 0),  # 1 AND 0 = 0
            (1, 1, 1),  # 1 AND 1 = 1
        ]

        for i, (x1, x2, expected) in enumerate(expected_results):
            assert X[i, 0] == x1 and X[i, 1] == x2, f"Input {i} should be [{x1}, {x2}]"
            assert y[i] == expected, f"Output {i} should be {expected}"

    def test_perceptron_default_config_solves_and(self):
        """The demo's preset values must end at 100 % accuracy.

        With epochs=5 the preset (lr 0.3, seed 42) stopped one epoch short at
        50 %, so the first thing a visitor saw was a model that had not
        learned. The values are read from perceptron.py itself so this fails
        if someone changes the preset without re-checking it.
        """
        import ast

        source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "perceptron.py"
        )
        with open(source_path, encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
        config = next(
            ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(getattr(target, "id", None) == "DEFAULT_CONFIG" for target in node.targets)
        )

        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
        y = np.array([0, 0, 0, 1])
        rng = np.random.default_rng(config["seed"])
        weights = rng.uniform(-1.0, 1.0, size=2)
        bias = float(rng.uniform(-1.0, 1.0))
        for _ in range(config["epochs"]):
            for features, target in zip(X, y, strict=True):
                prediction = 1 if float(features @ weights + bias) >= 0 else 0
                error = target - prediction
                weights = weights + config["lr"] * error * features
                bias += config["lr"] * error

        predictions = ((X @ weights + bias) >= 0).astype(int)
        assert np.array_equal(predictions, y), "Preset perceptron must classify all four AND rows"

    def test_perceptron_activation(self):
        """Test perceptron activation function."""

        # Simple threshold function
        def activate(z):
            return 1 if z > 0 else 0

        assert activate(1) == 1, "activate(1) should return 1"
        assert activate(-1) == 0, "activate(-1) should return 0"
        assert activate(0) == 0, "activate(0) should return 0"

    def test_perceptron_weight_update_positive_error(self):
        """Test perceptron weight update when y=1 and y_hat=0 (error=+1)."""
        # Given: y=1, y_hat=0, error = y - y_hat = 1
        w = np.array([0.5, 0.5])
        b = 0.0
        lr = 0.3
        x = np.array([1, 1])
        error = 1  # y=1, y_hat=0

        # Weight update: w += lr * error * x
        w_new = w + lr * error * x
        b_new = b + lr * error

        # Expected: w = [0.5 + 0.3*1*1, 0.5 + 0.3*1*1] = [0.8, 0.8]
        assert np.allclose(w_new, [0.8, 0.8]), f"Expected [0.8, 0.8], got {w_new}"
        assert b_new == pytest.approx(0.3), f"Expected 0.3, got {b_new}"

    def test_perceptron_weight_update_negative_error(self):
        """Test perceptron weight update when y=0 and y_hat=1 (error=-1)."""
        # Given: y=0, y_hat=1, error = y - y_hat = -1
        w = np.array([0.8, 0.8])
        b = 0.3
        lr = 0.3
        x = np.array([1, 0])
        error = -1  # y=0, y_hat=1

        # Weight update: w += lr * error * x
        w_new = w + lr * error * x
        b_new = b + lr * error

        # Expected: w = [0.8 + 0.3*(-1)*1, 0.8 + 0.3*(-1)*0] = [0.5, 0.8]
        assert np.allclose(w_new, [0.5, 0.8]), f"Expected [0.5, 0.8], got {w_new}"
        assert b_new == pytest.approx(0.0), f"Expected 0.0, got {b_new}"

    def test_perceptron_no_update_on_correct_prediction(self):
        """Test that weights don't change when prediction is correct."""
        w = np.array([0.5, 0.5])
        b = 0.1
        lr = 0.3
        x = np.array([0, 0])
        error = 0  # Correct prediction

        w_new = w + lr * error * x
        b_new = b + lr * error

        assert np.array_equal(w_new, w), "Weights should not change on correct prediction"
        assert b_new == b, "Bias should not change on correct prediction"

    def test_perceptron_forward_pass(self):
        """Test perceptron forward pass calculation."""
        w = np.array([1.5, 1.5])
        b = -2.0
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])

        def forward(x, w, b):
            z = np.dot(x, w) + b
            return 1 if z > 0 else 0

        # Test predictions
        # [0,0]: 0*1.5 + 0*1.5 - 2.0 = -2.0 -> 0
        # [0,1]: 0*1.5 + 1*1.5 - 2.0 = -0.5 -> 0
        # [1,0]: 1*1.5 + 0*1.5 - 2.0 = -0.5 -> 0
        # [1,1]: 1*1.5 + 1*1.5 - 2.0 = 1.0 -> 1
        expected = [0, 0, 0, 1]

        for i, x in enumerate(X):
            pred = forward(x, w, b)
            assert pred == expected[i], f"Prediction for {x} should be {expected[i]}, got {pred}"

    def test_perceptron_training_convergence(self):
        """Test that perceptron converges on AND problem."""
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([0, 0, 0, 1])

        np.random.seed(42)
        w = np.random.uniform(-1, 1, 2)
        b = np.random.uniform(-1, 1)
        lr = 0.3

        # Train for multiple epochs
        for _ in range(10):
            for i in range(len(X)):
                z = np.dot(X[i], w) + b
                y_hat = 1 if z > 0 else 0
                error = y[i] - y_hat
                w += lr * error * X[i]
                b += lr * error

        # Test that it learned the AND function
        predictions = []
        for x in X:
            z = np.dot(x, w) + b
            predictions.append(1 if z > 0 else 0)

        assert predictions == [
            0,
            0,
            0,
            1,
        ], f"Perceptron should learn AND, got {predictions}"

    def test_perceptron_weight_history(self):
        """Test that weight history is correctly recorded."""
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([0, 0, 0, 1])

        np.random.seed(42)
        w = np.random.uniform(-1, 1, 2)
        b = np.random.uniform(-1, 1)
        lr = 0.3

        history = [(w.copy(), b)]

        for _ in range(2):  # 2 epochs
            for i in range(len(X)):
                z = np.dot(X[i], w) + b
                y_hat = 1 if z > 0 else 0
                error = y[i] - y_hat
                w += lr * error * X[i]
                b += lr * error
                history.append((w.copy(), b))

        # Should have initial + (epochs * samples) entries
        expected_entries = 1 + 2 * 4  # 9 entries
        assert len(history) == expected_entries, f"Expected {expected_entries} history entries"


# =============================================================================
# KNN TESTS
# =============================================================================


class TestKNN:
    """Test KNN algorithm implementation."""

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""

        def euclidean_distance(p1, p2):
            return np.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2, strict=False)))

        # Test known distances
        assert euclidean_distance([0, 0], [3, 4]) == 5.0, "Distance should be 5"
        assert euclidean_distance([1, 1], [1, 1]) == 0.0, "Distance to self should be 0"

        # Test with numpy arrays
        p1 = np.array([0, 0])
        p2 = np.array([1, 1])
        expected_dist = np.sqrt(2)
        actual_dist = euclidean_distance(p1, p2)
        assert abs(actual_dist - expected_dist) < 1e-10, f"Distance should be {expected_dist}"

    def test_knn_classification_logic(self):
        """Test KNN classification logic."""
        # Mock k-nearest neighbors results
        neighbors = ["A", "A", "B"]  # 2 A's, 1 B

        # Count classes
        class_counts = {}
        for cls in neighbors:
            class_counts[cls] = class_counts.get(cls, 0) + 1

        # Find most common
        predicted_class = max(class_counts.keys(), key=lambda k: class_counts[k])

        assert predicted_class == "A", "Should predict class A (majority vote)"

    def test_knn_predict_deterministic_k1(self):
        """Test KNN prediction with k=1 (nearest neighbor)."""
        # Training points
        points = [
            (0.3, 0.3, "A"),
            (0.7, 0.7, "B"),
        ]

        # Test point close to class A
        test_point = (0.35, 0.35)
        k = 1

        # Calculate distances
        distances = []
        for px, py, cls in points:
            dist = np.sqrt((px - test_point[0]) ** 2 + (py - test_point[1]) ** 2)
            distances.append((dist, cls))

        distances.sort(key=lambda d: d[0])
        nearest_classes = [cls for _, cls in distances[:k]]
        predicted = max(set(nearest_classes), key=nearest_classes.count)

        assert predicted == "A", f"Point close to A should be classified as A, got {predicted}"

    def test_knn_predict_deterministic_k3(self):
        """Test KNN prediction with k=3."""
        # Training points: 3 A's clustered, 2 B's clustered
        points = [
            (0.1, 0.1, "A"),
            (0.2, 0.1, "A"),
            (0.1, 0.2, "A"),
            (0.8, 0.8, "B"),
            (0.9, 0.9, "B"),
        ]

        # Test point in the A cluster
        test_point = (0.15, 0.15)
        k = 3

        # Calculate distances and sort
        distances = []
        for px, py, cls in points:
            dist = np.sqrt((px - test_point[0]) ** 2 + (py - test_point[1]) ** 2)
            distances.append((dist, cls, px, py))

        distances.sort(key=lambda d: d[0])
        nearest_classes = [cls for _, cls, _, _ in distances[:k]]
        predicted = max(set(nearest_classes), key=nearest_classes.count)

        assert predicted == "A", f"Point near A cluster with k=3 should be A, got {predicted}"

    def test_knn_predict_boundary_case(self):
        """Test KNN prediction on class boundary."""
        # Equal distance to both classes
        points = [
            (0.0, 0.0, "A"),
            (1.0, 0.0, "B"),
        ]

        # Test point exactly in the middle
        test_point = (0.5, 0.0)

        distances = []
        for px, py, cls in points:
            dist = np.sqrt((px - test_point[0]) ** 2 + (py - test_point[1]) ** 2)
            distances.append((dist, cls))

        distances.sort(key=lambda d: d[0])

        # Both distances should be equal
        assert distances[0][0] == distances[1][0], "Distances should be equal on boundary"

    def test_knn_majority_vote_tie_breaker(self):
        """Test KNN tie-breaking behavior."""
        # k=2 with one A and one B neighbor
        neighbors = ["A", "B"]

        # max() returns first maximum in case of tie
        predicted = max(set(neighbors), key=neighbors.count)

        # With equal counts, it depends on iteration order - just verify it returns one of them
        assert predicted in ["A", "B"], "Should return one of the tied classes"

    def test_knn_distance_calculation_numpy(self):
        """Test distance calculation matching app implementation."""
        # Mimic the app's distance calculation
        ux, uy = 0.5, 0.5
        points = [(0.3, 0.3, "A"), (0.7, 0.7, "B")]

        distances = [
            (np.sqrt((px - ux) ** 2 + (py - uy) ** 2), cls, px, py) for px, py, cls in points
        ]
        distances.sort(key=lambda d: d[0])

        # Distance to (0.3, 0.3) = sqrt(0.04 + 0.04) = sqrt(0.08)
        # Distance to (0.7, 0.7) = sqrt(0.04 + 0.04) = sqrt(0.08)
        expected_dist = np.sqrt(0.08)

        assert distances[0][0] == pytest.approx(expected_dist), "Distance calculation mismatch"
        assert distances[1][0] == pytest.approx(expected_dist), "Distance calculation mismatch"

    def test_knn_predict_all_same_class(self):
        """Test KNN when all neighbors are same class."""
        points = [
            (0.1, 0.1, "A"),
            (0.2, 0.2, "A"),
            (0.3, 0.3, "A"),
        ]

        test_point = (0.15, 0.15)
        k = 3

        distances = []
        for px, py, cls in points:
            dist = np.sqrt((px - test_point[0]) ** 2 + (py - test_point[1]) ** 2)
            distances.append((dist, cls))

        distances.sort(key=lambda d: d[0])
        nearest_classes = [cls for _, cls in distances[:k]]
        predicted = max(set(nearest_classes), key=nearest_classes.count)

        assert predicted == "A", "Should predict A when all neighbors are A"
        assert nearest_classes.count("A") == 3, "All 3 neighbors should be class A"

    def test_knn_different_k_values(self):
        """Test KNN with different k values on same data."""
        # 2 A's close to test point, 3 B's further away
        points = [
            (0.1, 0.1, "A"),  # Closest
            (0.15, 0.15, "A"),  # Second closest
            (0.5, 0.5, "B"),  # Third
            (0.6, 0.6, "B"),  # Fourth
            (0.7, 0.7, "B"),  # Fifth
        ]

        test_point = (0.12, 0.12)

        def predict_knn(test_point, points, k):
            distances = []
            for px, py, cls in points:
                dist = np.sqrt((px - test_point[0]) ** 2 + (py - test_point[1]) ** 2)
                distances.append((dist, cls))
            distances.sort(key=lambda d: d[0])
            nearest_classes = [cls for _, cls in distances[:k]]
            return max(set(nearest_classes), key=nearest_classes.count)

        # k=1: Nearest is A
        assert predict_knn(test_point, points, 1) == "A", "k=1 should predict A"

        # k=3: 2 A's + 1 B -> A wins
        assert predict_knn(test_point, points, 3) == "A", "k=3 should predict A"

        # k=5: 2 A's + 3 B's -> B wins
        assert predict_knn(test_point, points, 5) == "B", "k=5 should predict B"

    def test_knn_insufficient_points_check(self):
        """Test that KNN requires at least k points."""
        points = [(0.5, 0.5, "A")]  # Only 1 point
        k = 3

        # Check that there aren't enough points
        assert len(points) < k, f"Should have fewer points than k ({k})"


# =============================================================================
# NEURAL NETWORK TESTS
# =============================================================================


class TestNeuralNetwork:
    """Test neural network implementation."""

    def test_sigmoid_function(self):
        """Test sigmoid activation function."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        # Test boundary values
        assert abs(sigmoid(0) - 0.5) < 1e-10, "sigmoid(0) should be 0.5"
        assert sigmoid(100) > 0.99, "sigmoid(large positive) should be close to 1"
        assert sigmoid(-100) < 0.01, "sigmoid(large negative) should be close to 0"

        # Test monotonicity
        assert sigmoid(-1) < sigmoid(0) < sigmoid(1), "Sigmoid should be monotonic"

    def test_sigmoid_numerical_stability(self):
        """Test sigmoid doesn't overflow with extreme values."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        # Should not raise overflow errors
        result_large_pos = sigmoid(1000)
        result_large_neg = sigmoid(-1000)

        assert result_large_pos == pytest.approx(1.0), "Large positive should return ~1"
        assert result_large_neg == pytest.approx(0.0), "Large negative should return ~0"

    def test_sigmoid_array_input(self):
        """Test sigmoid with numpy array input."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        x = np.array([-2, -1, 0, 1, 2])
        result = sigmoid(x)

        assert result.shape == x.shape, "Output shape should match input"
        assert result[2] == pytest.approx(0.5), "sigmoid(0) should be 0.5"
        assert all(0 < r < 1 for r in result), "All values should be in (0, 1)"

    def test_neural_network_forward_pass(self):
        """Test neural network forward pass."""
        # Simple 2-input network test
        inputs = np.array([1, 0])  # Input pattern

        # Hidden layer weights (2x2 matrix)
        weights_hidden = np.array([[1.5, 1.5], [1.5, 1.5]])
        bias_hidden = np.array([-2.25, -2.25])

        # Calculate hidden layer output
        hidden_raw = np.dot(weights_hidden, inputs) + bias_hidden

        expected_raw = np.array([1.5 - 2.25, 1.5 - 2.25])  # [-0.75, -0.75]
        assert np.allclose(hidden_raw, expected_raw), (
            f"Hidden raw should be {expected_raw}, got {hidden_raw}"
        )

    def test_neural_network_hidden_layer(self):
        """Test hidden layer calculation from neuronal-net.py."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        weights_hidden = np.array([[1.5, 1.5], [1.5, 1.5]])
        bias_hidden = np.array([-2.25, -2.25])

        # Test [1, 1] input (should activate AND)
        inputs = np.array([1, 1])
        hidden_raw = np.dot(weights_hidden, inputs) + bias_hidden
        hidden_activation = sigmoid(hidden_raw)

        # z = 1.5*1 + 1.5*1 - 2.25 = 0.75 for both neurons
        expected_raw = 0.75
        assert hidden_raw[0] == pytest.approx(expected_raw), f"Expected {expected_raw}"
        assert hidden_activation[0] > 0.5, "Hidden neuron should be activated for [1,1]"

    def test_neural_network_output_layer(self):
        """Test output layer calculation."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        weights_output = np.array([1.0, 1.0])
        bias_output = -0.5

        # Simulated hidden activation
        hidden_activation = np.array([0.68, 0.68])  # ~sigmoid(0.75)

        output_raw = np.dot(weights_output, hidden_activation) + bias_output
        output_activation = sigmoid(output_raw)

        # z = 1.0*0.68 + 1.0*0.68 - 0.5 = 0.86
        expected_z = 0.86
        assert output_raw == pytest.approx(expected_z, abs=0.1), f"Output z should be ~{expected_z}"
        assert output_activation > 0.5, "Output should be activated (predict 1)"

    def test_neural_network_and_truth_table(self):
        """Test neural network produces correct AND truth table."""

        def sigmoid(x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

        # Weights tuned to implement AND gate
        # Hidden layer acts as two AND-detecting neurons
        weights_hidden = np.array([[20.0, 20.0], [20.0, 20.0]])
        bias_hidden = np.array([-30.0, -30.0])  # Only activates when both inputs are 1
        weights_output = np.array([20.0, 20.0])
        bias_output = -10.0

        def forward(inputs):
            h_raw = np.dot(weights_hidden, inputs) + bias_hidden
            h_act = sigmoid(h_raw)
            o_raw = np.dot(weights_output, h_act) + bias_output
            o_act = sigmoid(o_raw)
            return 1 if o_act > 0.5 else 0

        # Test all AND combinations
        test_cases = [
            ([0, 0], 0),
            ([0, 1], 0),
            ([1, 0], 0),
            ([1, 1], 1),
        ]

        for inputs, expected in test_cases:
            result = forward(np.array(inputs))
            assert result == expected, (
                f"AND({inputs[0]}, {inputs[1]}) should be {expected}, got {result}"
            )

    def test_binary_and_training_data(self):
        """Test binary AND training data."""
        # All possible combinations for 2-input binary AND
        test_cases = [([0, 0], 0), ([0, 1], 0), ([1, 0], 0), ([1, 1], 1)]

        for inputs, expected in test_cases:
            actual = inputs[0] & inputs[1]  # Binary AND
            assert actual == expected, f"AND({inputs[0]}, {inputs[1]}) should be {expected}"

    def test_neural_network_weight_contribution(self):
        """Test individual weight contributions to layer output."""
        inputs = np.array([1, 1])
        weights_hidden = np.array([[1.5, 1.5], [1.5, 1.5]])

        # Contribution from each input to first hidden neuron
        contrib1 = weights_hidden[0, 0] * inputs[0]  # w1 * x1
        contrib2 = weights_hidden[0, 1] * inputs[1]  # w2 * x2

        assert contrib1 == 1.5, f"Contribution from x1 should be 1.5, got {contrib1}"
        assert contrib2 == 1.5, f"Contribution from x2 should be 1.5, got {contrib2}"
        assert contrib1 + contrib2 == 3.0, "Total contribution should be 3.0"


if __name__ == "__main__":
    # If pytest is not available, run basic tests manually
    print("Running basic algorithm tests...")

    # Test gradient descent
    gd = TestGradientDescent()
    try:
        gd.test_gradient_descent_function()
        gd.test_gradient_descent_derivative()
        gd.test_gradient_descent_convergence()
        gd.test_gradient_descent_loss_decreases()
        gd.test_gradient_descent_step_calculation()
        print("Gradient Descent tests passed")
    except Exception as e:
        print(f"Gradient Descent tests failed: {e}")

    # Test perceptron
    perceptron = TestPerceptron()
    try:
        perceptron.test_perceptron_and_training_data()
        perceptron.test_perceptron_activation()
        perceptron.test_perceptron_weight_update_positive_error()
        perceptron.test_perceptron_weight_update_negative_error()
        perceptron.test_perceptron_training_convergence()
        print("Perceptron tests passed")
    except Exception as e:
        print(f"Perceptron tests failed: {e}")

    # Test KNN
    knn = TestKNN()
    try:
        knn.test_euclidean_distance()
        knn.test_knn_classification_logic()
        knn.test_knn_predict_deterministic_k1()
        knn.test_knn_predict_deterministic_k3()
        knn.test_knn_different_k_values()
        print("KNN tests passed")
    except Exception as e:
        print(f"KNN tests failed: {e}")

    # Test neural network
    nn = TestNeuralNetwork()
    try:
        nn.test_sigmoid_function()
        nn.test_neural_network_forward_pass()
        nn.test_neural_network_and_truth_table()
        nn.test_binary_and_training_data()
        print("Neural Network tests passed")
    except Exception as e:
        print(f"Neural Network tests failed: {e}")

    print("\nAll basic tests completed!")
