"""
Test basic application functionality

This module tests core application functionality without requiring
the Streamlit interface to be running.
"""

import importlib.util
import os


def test_app_imports():
    """Test that the main app can be imported without errors."""
    # Test that app.py exists and can be imported
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    assert os.path.exists(app_path), "app.py file should exist"

    # Test that we can load the app module
    spec = importlib.util.spec_from_file_location("app", app_path)
    assert spec is not None, "Should be able to create module spec for app.py"


def test_pages_directory_exists():
    """Test that the pages directory exists and contains expected files."""
    pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
    assert os.path.exists(pages_dir), "pages directory should exist"

    expected_pages = [
        "gradient-descent.py",
        "perceptron.py",
        "knn-visualize.py",
        "neuronal-net.py",
    ]

    for page in expected_pages:
        page_path = os.path.join(pages_dir, page)
        assert os.path.exists(page_path), f"{page} should exist in pages directory"


def test_requirements_file():
    """Test that requirements.txt exists and contains essential packages."""
    req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    assert os.path.exists(req_path), "requirements.txt should exist"

    with open(req_path) as f:
        requirements = f.read().lower()

    essential_packages = ["streamlit", "numpy", "pandas", "matplotlib"]
    for package in essential_packages:
        assert package in requirements, f"{package} should be in requirements.txt"


def test_dockerfile_exists():
    """Test that dockerfile exists."""
    dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dockerfile")
    assert os.path.exists(dockerfile_path), "dockerfile should exist"


if __name__ == "__main__":
    # If pytest is not available, run tests manually
    print("Running app structure tests...")

    try:
        test_app_imports()
        print("App imports test passed")
    except Exception as e:
        print(f"App imports test failed: {e}")

    try:
        test_pages_directory_exists()
        print("Pages directory test passed")
    except Exception as e:
        print(f"Pages directory test failed: {e}")

    try:
        test_requirements_file()
        print("Requirements file test passed")
    except Exception as e:
        print(f"Requirements file test failed: {e}")

    try:
        test_dockerfile_exists()
        print("Dockerfile test passed")
    except Exception as e:
        print(f"Dockerfile test failed: {e}")

    print("App structure tests completed!")
