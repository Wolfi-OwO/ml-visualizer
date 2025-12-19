"""
Test utility functions and configuration

This module tests utility functions and configuration loading.
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestVersionFile:
    """Test VERSION file handling."""

    def test_version_file_exists(self):
        """Test that VERSION file exists in project root."""
        version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")
        assert os.path.exists(version_path), "VERSION file should exist"

    def test_version_format(self):
        """Test that VERSION file contains valid semantic version."""
        version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")

        with open(version_path) as f:
            version = f.read().strip()

        # Check basic format (e.g., 1.0.0)
        parts = version.split(".")
        assert len(parts) >= 2, f"Version should have at least major.minor format: {version}"

        # Check that parts are numeric
        for part in parts:
            assert part.isdigit() or "-" in part, f"Version parts should be numeric: {version}"

    def test_version_not_empty(self):
        """Test that VERSION file is not empty."""
        version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")

        with open(version_path) as f:
            version = f.read().strip()

        assert len(version) > 0, "VERSION file should not be empty"


class TestProjectStructure:
    """Test project structure and organization."""

    def test_src_directory_exists(self):
        """Test that src directory exists."""
        src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
        assert os.path.exists(src_path), "src directory should exist"

    def test_pages_directory_exists(self):
        """Test that pages directory exists."""
        pages_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        assert os.path.exists(pages_path), "pages directory should exist"

    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        tests_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests")
        assert os.path.exists(tests_path), "tests directory should exist"

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Dockerfile")
        assert os.path.exists(dockerfile_path), "Dockerfile should exist"

    def test_gitignore_exists(self):
        """Test that .gitignore exists."""
        gitignore_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".gitignore")
        assert os.path.exists(gitignore_path), ".gitignore should exist"


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_default_environment(self):
        """Test default environment handling when no env var is set."""
        # Save current environment
        original_env = os.environ.get("ENVIRONMENT")

        try:
            # Remove ENVIRONMENT var if it exists
            if "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

            # Should default to production or development
            env = os.environ.get("ENVIRONMENT", "production")
            assert env in [
                "production",
                "development",
                "staging",
                "testing",
            ], f"Environment should be valid: {env}"

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["ENVIRONMENT"] = original_env

    def test_environment_values(self):
        """Test that valid environment values are recognized."""
        valid_envs = ["development", "testing", "staging", "production"]

        for env in valid_envs:
            os.environ["ENVIRONMENT"] = env
            assert os.environ.get("ENVIRONMENT") == env, f"Environment should be set to {env}"


class TestPythonVersion:
    """Test Python version compatibility."""

    def test_python_version(self):
        """Test that Python version is 3.10 or higher."""
        import sys

        major, minor = sys.version_info[:2]
        assert major == 3, "Python major version should be 3"
        assert minor >= 10, f"Python minor version should be >= 10, got {minor}"


class TestDependencies:
    """Test that required dependencies are available."""

    def test_numpy_import(self):
        """Test that numpy can be imported."""
        try:
            import numpy

            assert hasattr(numpy, "__version__"), "numpy should have a version"
        except ImportError:
            pytest.fail("numpy should be importable")

    def test_pandas_import(self):
        """Test that pandas can be imported."""
        try:
            import pandas

            assert hasattr(pandas, "__version__"), "pandas should have a version"
        except ImportError:
            pytest.fail("pandas should be importable")

    def test_matplotlib_import(self):
        """Test that matplotlib can be imported."""
        try:
            import matplotlib

            assert hasattr(matplotlib, "__version__"), "matplotlib should have a version"
        except ImportError:
            pytest.fail("matplotlib should be importable")

    def test_streamlit_import(self):
        """Test that streamlit can be imported."""
        try:
            import streamlit

            assert hasattr(streamlit, "__version__"), "streamlit should have a version"
        except ImportError:
            pytest.fail("streamlit should be importable")


if __name__ == "__main__":
    print("Running utility tests...")

    # VERSION tests
    version_test = TestVersionFile()
    try:
        version_test.test_version_file_exists()
        print("✓ VERSION file exists")
    except AssertionError as e:
        print(f"✗ VERSION file test failed: {e}")

    try:
        version_test.test_version_format()
        print("✓ VERSION format valid")
    except AssertionError as e:
        print(f"✗ VERSION format test failed: {e}")

    # Project structure tests
    structure_test = TestProjectStructure()
    try:
        structure_test.test_src_directory_exists()
        structure_test.test_pages_directory_exists()
        structure_test.test_tests_directory_exists()
        print("✓ Project structure valid")
    except AssertionError as e:
        print(f"✗ Project structure test failed: {e}")

    # Dependency tests
    deps_test = TestDependencies()
    try:
        deps_test.test_numpy_import()
        deps_test.test_pandas_import()
        deps_test.test_matplotlib_import()
        deps_test.test_streamlit_import()
        print("✓ All dependencies available")
    except Exception as e:
        print(f"✗ Dependency test failed: {e}")

    print("Utility tests completed!")
