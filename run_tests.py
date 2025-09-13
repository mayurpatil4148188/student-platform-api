#!/usr/bin/env python3
"""
Test Runner Script for Student Platform API
Provides easy commands to run different types of tests.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test runner for Student Platform API")
    parser.add_argument(
        "test_type",
        choices=[
            "all", "unit", "integration", "api", "model", "service",
            "coverage", "fast", "slow", "students", "applications", "status"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run with verbose output"
    )
    parser.add_argument(
        "--stop-on-fail", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        default=0,
        help="Number of parallel workers (0 to disable, requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("FLASK_ENV", "testing")
    
    # Base pytest command
    base_cmd = "pytest"
    
    # Add options based on arguments
    if args.verbose:
        base_cmd += " -vv"
    
    if args.stop_on_fail:
        base_cmd += " -x"
    
    if args.parallel > 0:
        base_cmd += f" -n {args.parallel}"
    
    # Define test commands
    commands = {
        "all": f"{base_cmd}",
        "unit": f"{base_cmd} -m unit",
        "integration": f"{base_cmd} -m integration",
        "api": f"{base_cmd} -m api",
        "model": f"{base_cmd} -m model",
        "service": f"{base_cmd} -m service",
        "coverage": f"{base_cmd} --cov=app --cov-report=html --cov-report=term-missing",
        "fast": f"{base_cmd} -m 'not slow'",
        "slow": f"{base_cmd} -m slow",
        "students": f"{base_cmd} tests/test_students.py",
        "applications": f"{base_cmd} tests/test_applications.py",
        "status": f"{base_cmd} tests/test_status_calculator.py"
    }
    
    command = commands.get(args.test_type, f"{base_cmd}")
    
    # Run the tests
    success = run_command(command, f"Running {args.test_type} tests")
    
    if args.test_type == "coverage" and success:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
        print("Open the file in your browser to view detailed coverage.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
