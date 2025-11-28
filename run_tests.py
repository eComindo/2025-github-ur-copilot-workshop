#!/usr/bin/env python3
"""
Test runner script for the Pomodoro Timer application.
This script provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import os


def run_command(command, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True)
    return result.returncode == 0


def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    # Ensure we're in the virtual environment
    if not os.path.exists('.venv'):
        print("Error: Virtual environment not found. Please run 'uv venv' first.")
        sys.exit(1)
    
    # Base pytest command
    base_cmd = '"D:/Ecomindo/GH Universe/2025-github-ur-copilot-workshop/.venv/Scripts/python.exe" -m pytest'
    
    success = True
    
    if test_type == "unit" or test_type == "all":
        success &= run_command(
            f'{base_cmd} tests/test_app.py -v',
            "Unit Tests"
        )
    
    if test_type == "integration" or test_type == "all":
        success &= run_command(
            f'{base_cmd} tests/test_integration.py -v',
            "Integration Tests"
        )
    
    if test_type == "coverage" or test_type == "all":
        success &= run_command(
            f'{base_cmd} --cov=app --cov-report=term-missing --cov-report=html',
            "Coverage Report"
        )
    
    if test_type == "quick":
        success &= run_command(
            f'{base_cmd} -x',
            "Quick Test Run (stop on first failure)"
        )
    
    if test_type == "verbose":
        success &= run_command(
            f'{base_cmd} -v -s',
            "Verbose Test Run"
        )
    
    if test_type == "help":
        print("""
Test Runner Usage:
    python run_tests.py [test_type]

Available test types:
    all         - Run all tests with coverage (default)
    unit        - Run unit tests only
    integration - Run integration tests only
    coverage    - Run tests with detailed coverage report
    quick       - Run tests until first failure
    verbose     - Run tests with verbose output
    help        - Show this help message

Examples:
    python run_tests.py
    python run_tests.py unit
    python run_tests.py coverage
    python run_tests.py quick
        """)
        return
    
    if success:
        print(f"\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()