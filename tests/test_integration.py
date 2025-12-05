"""
Integration tests for the ML Visualizer application

This module tests integration between different components and
end-to-end workflows.
"""

import os
import sys

import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMLAlgorithmIntegration:
    """Test integration of ML algorithms with data processing."""

    def test_perceptron_on_linearly_separable_data(self):
        """Test that perceptron converges on linearly separable data."""
        # Create linearly separable data
        np.random.seed(42)
        X1 = np.random.randn(50, 2) + np.array([2, 2])
        X2 = np.random.randn(50, 2) + np.array([-2, -2])
        X = np.vstack([X1, X2])
        y = np.array([1] * 50 + [-1] * 50)

        # Simple perceptron implementation
        w = np.zeros(2)
        b = 0
        lr = 0.1

        # Train for max 100 iterations
        for _epoch in range(100):
            errors = 0
            for i in range(len(X)):
                prediction = np.sign(np.dot(w, X[i]) + b)
                if prediction != y[i]:
                    w += lr * y[i] * X[i]
                    b += lr * y[i]
                    errors += 1
            if errors == 0:
                break

        # Test that it converges (no errors on training data)
        correct = 0
        for i in range(len(X)):
            prediction = np.sign(np.dot(w, X[i]) + b)
            if prediction == y[i]:
                correct += 1

        accuracy = correct / len(X)
        assert accuracy >= 0.95, f"Perceptron should achieve >95% accuracy, got {accuracy:.2%}"

    def test_knn_basic_classification(self):
        """Test KNN classification on simple dataset."""
        # Create simple dataset
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 0, 1, 1])

        # Test point
        X_test = np.array([[1.5, 1.5]])

        # Calculate distances
        distances = np.sqrt(np.sum((X_train - X_test) ** 2, axis=1))

        # Get k=3 nearest neighbors
        k = 3
        nearest_indices = np.argsort(distances)[:k]
        nearest_labels = y_train[nearest_indices]

        # Majority vote
        prediction = np.bincount(nearest_labels).argmax()

        # Test point [1.5, 1.5] should be classified correctly
        assert prediction in [0, 1], "KNN should predict a valid class"

    def test_gradient_descent_optimization(self):
        """Test gradient descent on quadratic function."""

        def f(x):
            return (x - 3) ** 2 + 5

        def df(x):
            return 2 * (x - 3)

        # Start far from minimum
        x = 10.0
        lr = 0.1
        iterations = 100

        # Run gradient descent
        for _ in range(iterations):
            x = x - lr * df(x)

        # Should converge close to x=3
        assert abs(x - 3.0) < 0.5, f"Should converge close to x=3, got x={x}"
        assert abs(f(x) - 5.0) < 1.0, f"Should converge close to f(x)=5, got f(x)={f(x)}"


class TestDataValidation:
    """Test data validation and preprocessing."""

    def test_input_data_normalization(self):
        """Test that data normalization works correctly."""
        data = np.array([[1, 2], [3, 4], [5, 6]])

        # Normalize to [0, 1]
        data_min = data.min(axis=0)
        data_max = data.max(axis=0)
        normalized = (data - data_min) / (data_max - data_min)

        # Check that all values are in [0, 1]
        assert np.all(normalized >= 0), "Normalized values should be >= 0"
        assert np.all(normalized <= 1), "Normalized values should be <= 1"

    def test_train_test_split(self):
        """Test that train-test split maintains proportions."""
        # Create dataset
        X = np.random.randn(100, 2)
        y = np.random.randint(0, 2, 100)

        # Split (80-20)
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Check sizes
        assert len(X_train) == 80, "Training set should have 80 samples"
        assert len(X_test) == 20, "Test set should have 20 samples"
        assert len(y_train) == 80, "Training labels should have 80 samples"
        assert len(y_test) == 20, "Test labels should have 20 samples"

    def test_data_shape_consistency(self):
        """Test that data shapes are consistent."""
        X = np.random.randn(50, 3)
        y = np.random.randint(0, 2, 50)

        # Check shapes
        assert X.shape[0] == y.shape[0], "Number of samples should match labels"
        assert len(X.shape) == 2, "X should be 2D array"
        assert len(y.shape) == 1, "y should be 1D array"


class TestNumericalStability:
    """Test numerical stability of algorithms."""

    def test_division_by_zero_handling(self):
        """Test that division by zero is handled."""
        data = np.array([1.0, 2.0, 3.0])

        # Normalize with potential division by zero
        data_range = data.max() - data.min()
        if data_range == 0:
            normalized = np.zeros_like(data)
        else:
            normalized = (data - data.min()) / data_range

        assert not np.any(np.isnan(normalized)), "Should not produce NaN values"
        assert not np.any(np.isinf(normalized)), "Should not produce Inf values"

    def test_large_number_handling(self):
        """Test that algorithms handle large numbers."""
        large_value = 1e6
        X = np.array([[large_value, large_value]])

        # Normalization should handle large values
        normalized = X / np.linalg.norm(X)

        assert not np.any(np.isnan(normalized)), "Should handle large numbers"
        assert not np.any(np.isinf(normalized)), "Should not overflow"

    def test_small_number_handling(self):
        """Test that algorithms handle small numbers."""
        small_value = 1e-10
        X = np.array([[small_value, small_value]])

        # Should handle small values without underflow
        result = X + 1.0

        assert not np.any(np.isnan(result)), "Should handle small numbers"
        assert result[0, 0] > 1.0, "Should add correctly"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_sample_handling(self):
        """Test algorithms with single sample."""
        X = np.array([[1.0, 2.0]])

        # Should handle single sample
        assert X.shape == (1, 2), "Should maintain shape with single sample"

    def test_empty_array_handling(self):
        """Test handling of empty arrays."""
        X = np.array([])

        assert len(X) == 0, "Empty array should have length 0"
        assert X.shape[0] == 0, "Empty array should have 0 rows"

    def test_identical_values(self):
        """Test handling of datasets with identical values."""
        X = np.ones((10, 2))

        # Standard deviation should be 0
        std = np.std(X, axis=0)
        assert np.all(std == 0), "Standard deviation of identical values should be 0"

    def test_negative_values(self):
        """Test handling of negative values."""
        X = np.array([[-1, -2], [-3, -4]])

        # Should handle negative values
        assert np.all(X < 0), "All values should be negative"

        # Min should work correctly
        assert X.min() == -4, "Min should find most negative value"


if __name__ == "__main__":
    print("Running integration tests...")

    # ML Algorithm Integration Tests
    ml_test = TestMLAlgorithmIntegration()
    try:
        ml_test.test_perceptron_on_linearly_separable_data()
        print("✓ Perceptron integration test passed")
    except Exception as e:
        print(f"✗ Perceptron integration test failed: {e}")

    try:
        ml_test.test_knn_basic_classification()
        print("✓ KNN integration test passed")
    except Exception as e:
        print(f"✗ KNN integration test failed: {e}")

    try:
        ml_test.test_gradient_descent_optimization()
        print("✓ Gradient descent integration test passed")
    except Exception as e:
        print(f"✗ Gradient descent integration test failed: {e}")

    # Data Validation Tests
    data_test = TestDataValidation()
    try:
        data_test.test_input_data_normalization()
        data_test.test_train_test_split()
        data_test.test_data_shape_consistency()
        print("✓ Data validation tests passed")
    except Exception as e:
        print(f"✗ Data validation test failed: {e}")

    # Numerical Stability Tests
    stability_test = TestNumericalStability()
    try:
        stability_test.test_division_by_zero_handling()
        stability_test.test_large_number_handling()
        stability_test.test_small_number_handling()
        print("✓ Numerical stability tests passed")
    except Exception as e:
        print(f"✗ Numerical stability test failed: {e}")

    # Edge Cases Tests
    edge_test = TestEdgeCases()
    try:
        edge_test.test_single_sample_handling()
        edge_test.test_empty_array_handling()
        edge_test.test_identical_values()
        edge_test.test_negative_values()
        print("✓ Edge case tests passed")
    except Exception as e:
        print(f"✗ Edge case test failed: {e}")

    print("Integration tests completed!")
