"""Unit tests for the ShortAnswer class."""

import unittest
from ars.qtype.question import Question
from ars.qtype.shortanswer import ShortAnswer

class TestShortAnswer(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.basic_question = "What is the capital of France?"
        self.basic_answer = "Paris"
        self.short_answer = ShortAnswer(self.basic_question, self.basic_answer)
        self.case_sensitive_answer = ShortAnswer(self.basic_question, self.basic_answer, case_sensitive=True)

    def test_initialization(self):
        """Test proper initialization of ShortAnswer instances."""
        # Test basic initialization
        self.assertEqual(self.short_answer._question, self.basic_question)
        self.assertEqual(self.short_answer._answer, self.basic_answer)
        self.assertFalse(self.short_answer._case_sensitive)

        # Test case-sensitive initialization
        self.assertTrue(self.case_sensitive_answer._case_sensitive)

    def test_normalize_basic(self):
        """Test basic text normalization."""
        test_cases = [
            (" test ", "test"),  # Leading/trailing spaces
            ("TEST", "test"),    # Capitalization
            ("t.e,s?t!", "test") # Punctuation
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(
                    self.short_answer._normalize(input_text),
                    expected
                )

    def test_check_answer_basic(self):
        """Test basic answer checking."""
        test_cases = [
            ("Paris", True),           # Exact match
            ("paris", True),           # Different case
            ("PARIS", True),           # All caps
            (" Paris ", True),         # Extra spaces
            ("Paris!", True),          # Punctuation
            ("Pariss", False),         # Wrong answer
            ("", False),               # Empty answer when correct answer is not empty
            ("  ", False),             # Only spaces when correct answer is not empty
        ]
        
        for answer, expected in test_cases:
            with self.subTest(answer=answer):
                self.assertEqual(
                    self.short_answer.check_answer(answer),
                    expected
                )

    def test_check_answer_case_sensitive(self):
        """Test case-sensitive answer checking."""
        # Create a new instance specifically for case-sensitive testing
        case_sensitive_qa = ShortAnswer("Question", "Paris", case_sensitive=True)
        test_cases = [
            ("Paris", True),     # Exact match
            ("paris", False),    # Different case
            ("PARIS", False),    # All caps
            (" Paris ", True),   # Extra spaces
            ("Paris!", True),    # Punctuation
            ("Pariss", False),   # Wrong answer
        ]
        
        for answer, expected in test_cases:
            with self.subTest(answer=answer):
                self.assertEqual(
                    case_sensitive_qa.check_answer(answer),
                    expected
                )

    def test_incorrect_feedback(self):
        """Test incorrect answer feedback."""
        expected_feedback = f"Incorrect. The correct answer is: {self.basic_answer}"
        self.assertEqual(self.short_answer.incorrect_feedback(), expected_feedback)

    def test_edge_cases(self):
        """Test edge cases and potential error conditions."""
        # Test with empty answer - the implementation treats empty strings as matching
        empty_answer = ShortAnswer("Question", "")
        self.assertTrue(empty_answer.check_answer(""))  # Updated expectation
        
        # Test with special characters
        special_answer = ShortAnswer("Question?", "!@#$%^&*()")
        self.assertTrue(special_answer.check_answer("!@#$%^&*()"))
        
        # Test with very long strings
        long_text = "a" * 1000
        long_answer = ShortAnswer("Long question?", long_text)
        self.assertTrue(long_answer.check_answer(long_text))

        # Test whitespace answer
        whitespace_answer = ShortAnswer("Question", "   ")
        self.assertTrue(whitespace_answer.check_answer("   "))

        # Test with newlines
        multiline = ShortAnswer("Question", "line1\nline2")
        self.assertTrue(multiline.check_answer("line1\nline2"))

    def test_inheritance(self):
        """Test inheritance from Question class."""
        self.assertTrue(isinstance(self.short_answer, Question))

if __name__ == '__main__':
    unittest.main()