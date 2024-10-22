from pathlib import Path
import unittest
import sys
import argparse

def setup_python_path():
    """Add the source directory to PYTHONPATH."""
    src_path = Path(__file__).parent / "quizme"
    sys.path.insert(0, str(src_path.resolve()))
    print(sys.path)

def run_specific_test(test_file: str) -> None:
    """
    Run a specific test file.
    
    Args:
        test_file (str): Name of the test file to run
    """
    # Convert filename to proper pattern if needed
    if not test_file.startswith("tests_"):
        test_file = f"tests_{test_file}"
    if not test_file.endswith(".py"):
        test_file = f"{test_file}.py"
    
    # Create test suite for specific file
    test_suite = unittest.defaultTestLoader.discover(
        "tests",
        pattern=test_file
    )
    
    if not list(test_suite):
        print(f"No tests found matching pattern: {test_file}")
        return
    
    unittest.TextTestRunner().run(test_suite)

def run_all_tests() -> None:
    """Run all test files matching pattern tests_*.py"""
    test_suite = unittest.defaultTestLoader.discover(
        "tests",
        pattern="tests_*.py"
    )
    unittest.TextTestRunner().run(test_suite)

def main():
    """Main function to handle test running."""
    parser = argparse.ArgumentParser(description="Run tests for QuizMe")
    parser.add_argument(
        "test_file",
        nargs="?",
        help="Specific test file to run (optional). If not provided, runs all tests."
    )
    
    args = parser.parse_args()
    
    # Setup Python path
    setup_python_path()
    
    # Run tests based on input
    if args.test_file:
        run_specific_test(args.test_file)
    else:
        run_all_tests()

if __name__ == "__main__":
    main()