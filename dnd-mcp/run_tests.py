#!/usr/bin/env python3
"""
Run all tests for the D&D Knowledge Navigator.
"""

import os
import sys
import unittest
import glob


def run_tests():
    """Run all test files in the tests directory."""
    print("Running D&D Knowledge Navigator tests...")

    # Add the current directory to the path so tests can import modules
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
