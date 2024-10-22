from pathlib import Path
import unittest
import sys

# Add the src directory to PYTHONPATH
src_path = Path(__file__).parent / "quizme"
sys.path.insert(0, str(src_path.resolve()))
print(sys.path)

# Discover and run tests
test_suite = unittest.defaultTestLoader.discover("tests", pattern="tests_*.py")
unittest.TextTestRunner().run(test_suite)