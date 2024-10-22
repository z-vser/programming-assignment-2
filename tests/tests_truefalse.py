import unittest
from ars.qtype.question import Question
from ars.qtype.truefalse import TrueFalse


class TestTrueFalse(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.question_text = "The sky is blue"
        self.explanation = "The sky appears blue due to Rayleigh scattering"
        self.true_question = TrueFalse(self.question_text, True, self.explanation)
        self.false_question = TrueFalse("The Earth is flat", False, "The Earth is approximately spherical")
        
    def test_initialization(self):
        """Test proper initialization of TrueFalse instances."""
        # Test basic initialization
        self.assertEqual(self.true_question._question, self.question_text)
        self.assertEqual(self.true_question._answer, True)
        self.assertEqual(self.true_question._explanation, self.explanation)
        
        # Test initialization without explanation
        no_explanation = TrueFalse("Test question", False)
        self.assertEqual(no_explanation._explanation, "")
        
        # Test invalid answer type
        with self.assertRaises(ValueError):
            TrueFalse("Invalid answer", "True")  # String instead of bool
        with self.assertRaises(ValueError):
            TrueFalse("Invalid answer", 1)  # Integer instead of bool
            
    def test_inheritance(self):
        """Test inheritance from Question class."""
        self.assertTrue(isinstance(self.true_question, Question))
        
    def test_ask(self):
        """Test the ask method."""
        expected = f"{self.question_text} (True/False)"
        self.assertEqual(self.true_question.ask(), expected)
        
    def test_check_answer_true_variations(self):
        """Test checking answers for a true question with various inputs."""
        true_variations = [
            "True", "true", "TRUE", "T", "t",
            "  True  ", "  T  ",  # with whitespace
        ]
        for answer in true_variations:
            with self.subTest(answer=answer):
                self.assertTrue(self.true_question.check_answer(answer))
                
    def test_check_answer_false_variations(self):
        """Test checking answers for a false question with various inputs."""
        false_variations = [
            "False", "false", "FALSE", "F", "f",
            "  False  ", "  F  ",  # with whitespace
        ]
        for answer in false_variations:
            with self.subTest(answer=answer):
                self.assertTrue(self.false_question.check_answer(answer))
                
    def test_incorrect_answers(self):
        """Test responses for incorrect answers."""
        # Test incorrect answers for true question
        false_variations = ["False", "false", "F", "f"]
        for answer in false_variations:
            with self.subTest(answer=answer):
                self.assertFalse(self.true_question.check_answer(answer))
                
        # Test incorrect answers for false question
        true_variations = ["True", "true", "T", "t"]
        for answer in true_variations:
            with self.subTest(answer=answer):
                self.assertFalse(self.false_question.check_answer(answer))
                
    def test_invalid_answers(self):
        """Test handling of invalid answers."""
        invalid_answers = [
            "Yes", "No",
            "1", "0",
            "", " ",
            "Truee", "Falsee",
            "TRUE/FALSE"
        ]
        for answer in invalid_answers:
            with self.subTest(answer=answer):
                with self.assertRaises(ValueError):
                    self.true_question.check_answer(answer)
                    
    def test_incorrect_feedback(self):
        """Test feedback for incorrect answers."""
        # Test with explanation
        expected_feedback = f"Incorrect. {self.explanation}"
        self.assertEqual(self.true_question.incorrect_feedback(), expected_feedback)
        
        # Test without explanation
        no_explanation = TrueFalse("Test question", True)
        self.assertEqual(no_explanation.incorrect_feedback(), "Incorrect. ")
        
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with empty question
        empty_q = TrueFalse("", True)
        self.assertEqual(empty_q.ask(), " (True/False)")
        
        # Test with very long question
        long_q = TrueFalse("q" * 1000, True)
        self.assertEqual(long_q.ask(), "q" * 1000 + " (True/False)")
        
        # Test with very long explanation
        long_exp = TrueFalse("Question", True, "e" * 1000)
        self.assertEqual(long_exp.incorrect_feedback(), "Incorrect. " + "e" * 1000)
        
        # Test with special characters in question
        special_q = TrueFalse("!@#$%^&*()", True)
        self.assertEqual(special_q.ask(), "!@#$%^&*() (True/False)")

if __name__ == '__main__':
    unittest.main()