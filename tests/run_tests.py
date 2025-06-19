#!/usr/bin/env python3
"""
Test runner for PDF Reader package.

This script runs all tests for the PDF Reader package and provides
a summary of results.
"""

import sys
import unittest
from pathlib import Path
from test_refactored_package import TestPDFReaderPackage
from test_with_mock_pdfs import TestWithMockPDFs

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests() -> unittest.TestResult:
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(TestPDFReaderPackage))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWithMockPDFs))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


if __name__ == "__main__":
    print("Running PDF Reader Package Tests")
    print("=" * 50)

    result = run_tests()

    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    sys.exit(len(result.failures) + len(result.errors))
