#!/usr/bin/env python3
"""
Simple test runner for the PDF Reader package.
"""

import os
import sys
import subprocess


def main():
    """Run the comprehensive test suite."""
    print("PDF READER PACKAGE - TEST RUNNER")
    print("=" * 50)
    
    # Change to tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the comprehensive test script
    try:
        subprocess.run([sys.executable, "test_with_mock_pdfs.py"], check=True)
        print("\n✅ All tests completed successfully!")
        return 0
    except subprocess.CalledProcessError:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 