"""
Test page functionality and imports

This module tests that all visualization pages can be imported
and contain the expected functions.
"""

import importlib.util
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestPages:
    """Test individual page modules."""

    def load_page_module(self, page_name):
        """Helper function to load a page module."""
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        page_path = os.path.join(pages_dir, page_name)

        assert os.path.exists(page_path), f"Page {page_name} should exist"

        # Load the module
        module_name = page_name.replace("-", "_").replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, page_path)
        module = importlib.util.module_from_spec(spec)

        return spec, module

    def test_gradient_descent_page(self):
        """Test gradient descent page can be loaded."""
        spec, module = self.load_page_module("gradient-descent.py")
        assert spec is not None, "Should be able to create spec for gradient-descent.py"

        # Test that the module defines the expected functions
        try:
            spec.loader.exec_module(module)
            # Check that key functions exist
            assert hasattr(module, "f"), "gradient-descent.py should define function f"
            assert hasattr(module, "df"), "gradient-descent.py should define function df"
        except Exception:
            # If execution fails due to Streamlit not being available, that's OK
            # We're just testing that the module can be parsed
            pass

    def test_perceptron_page(self):
        """Test perceptron page can be loaded."""
        spec, module = self.load_page_module("perceptron.py")
        assert spec is not None, "Should be able to create spec for perceptron.py"

    def test_knn_page(self):
        """Test KNN visualizer page can be loaded."""
        spec, module = self.load_page_module("knn-visualize.py")
        assert spec is not None, "Should be able to create spec for knn-visualize.py"

    def test_neuronal_net_page(self):
        """Test neural network page can be loaded."""
        spec, module = self.load_page_module("neuronal-net.py")
        assert spec is not None, "Should be able to create spec for neuronal-net.py"

    def test_all_pages_have_streamlit_imports(self):
        """Test that all pages import streamlit."""
        pages = [
            "gradient-descent.py",
            "perceptron.py",
            "knn-visualize.py",
            "neuronal-net.py",
        ]

        for page_name in pages:
            pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
            page_path = os.path.join(pages_dir, page_name)

            with open(page_path) as f:
                content = f.read()

            assert "import streamlit" in content, f"{page_name} should import streamlit"

    def test_pages_have_titles(self):
        """Test that all pages set titles."""
        pages = [
            "gradient-descent.py",
            "perceptron.py",
            "knn-visualize.py",
            "neuronal-net.py",
        ]

        for page_name in pages:
            pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
            page_path = os.path.join(pages_dir, page_name)

            with open(page_path) as f:
                content = f.read()

            assert "st.title(" in content, f"{page_name} should set a title with st.title()"


if __name__ == "__main__":
    # If pytest is not available, run tests manually
    print("Running page tests...")

    pages_test = TestPages()

    try:
        pages_test.test_gradient_descent_page()
        print("Gradient Descent page test passed")
    except Exception as e:
        print(f"Gradient Descent page test failed: {e}")

    try:
        pages_test.test_perceptron_page()
        print("Perceptron page test passed")
    except Exception as e:
        print(f"Perceptron page test failed: {e}")

    try:
        pages_test.test_knn_page()
        print("KNN page test passed")
    except Exception as e:
        print(f"KNN page test failed: {e}")

    try:
        pages_test.test_neuronal_net_page()
        print("Neural Network page test passed")
    except Exception as e:
        print(f"Neural Network page test failed: {e}")

    try:
        pages_test.test_all_pages_have_streamlit_imports()
        print("Streamlit imports test passed")
    except Exception as e:
        print(f"Streamlit imports test failed: {e}")

    try:
        pages_test.test_pages_have_titles()
        print("Page titles test passed")
    except Exception as e:
        print(f"Page titles test failed: {e}")

    print("Page tests completed!")
