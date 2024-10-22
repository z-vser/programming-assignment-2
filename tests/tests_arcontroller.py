import unittest
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime, timedelta
from ars.arcontroller import ARController
from ars.boxmanager import BoxManager
from ars.qtype.shortanswer import ShortAnswer
from ars.qtype.truefalse import TrueFalse

class TestARController(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.sample_questions = [
            {
                "type": "shortanswer",
                "question": "What is the capital of France?",
                "correct_answer": "Paris",
                "case_sensitive": False
            },
            {
                "type": "truefalse",
                "question": "The Earth is flat",
                "correct_answer": False,
                "explanation": "The Earth is approximately spherical"
            },
            {
                "type": "shortanswer",
                "question": "What is 2+2?",
                "correct_answer": "4"
            }
        ]
        self.controller = ARController(self.sample_questions)

    def test_initialization(self):
        """Test proper initialization of ARController."""
        # Verify BoxManager is initialized
        self.assertIsInstance(self.controller._box_manager, BoxManager)
        
        # Check if questions were added to unasked box
        unasked_box = self.controller._box_manager._boxes[1]
        self.assertEqual(len(unasked_box._questions), 3)

    def test_question_creation(self):
        """Test creation of different question types."""
        # Initialize with one of each type
        questions = [
            {
                "type": "shortanswer",
                "question": "Test SA",
                "correct_answer": "answer",
                "case_sensitive": True
            },
            {
                "type": "truefalse",
                "question": "Test TF",
                "correct_answer": True,
                "explanation": "explanation"
            }
        ]
        
        controller = ARController(questions)
        unasked_box = controller._box_manager._boxes[1]
        
        # Verify questions were created with correct types
        questions_list = unasked_box._questions
        question_types = {type(q) for q in questions_list}
        self.assertEqual(question_types, {ShortAnswer, TrueFalse})

    def test_invalid_question_type(self):
        """Test handling of invalid question type."""
        with patch('builtins.print') as mock_print:
            questions = [
                {
                    "type": "invalid",
                    "question": "Test",
                    "correct_answer": "answer"
                }
            ]
            controller = ARController(questions)
            mock_print.assert_called_with("Unsupported question type: invalid. Skipping this question.")
            self.assertEqual(len(controller._box_manager._boxes[1]._questions), 0)

    def test_missing_required_fields(self):
        """Test handling of questions with missing required fields."""
        with patch('builtins.print') as mock_print:
            questions = [
                {
                    "type": "shortanswer",
                    "question": "Test"  # missing correct_answer
                }
            ]
            controller = ARController(questions)
            mock_print.assert_called_with(
                "Missing required field for question: 'correct_answer'. Skipping this question."
            )
            self.assertEqual(len(controller._box_manager._boxes[1]._questions), 0)

    def test_start_session_quit(self):
        """Test quitting the session."""
        with patch('builtins.print') as mock_print, \
             patch('builtins.input', return_value='q') as mock_input:
            
            self.controller.start()
            mock_input.assert_called_once()
            mock_print.assert_called_with("Thank you, goodbye!")

    def test_start_session_complete(self):
        """Test completing all questions."""
        # Move all questions to Known Questions box
        for question in self.controller._box_manager._boxes[1]._questions.copy():
            for _ in range(3):
                self.controller._box_manager.move_question(question, True)
        
        with patch('builtins.print') as mock_print:
            self.controller.start()
            # Verify the complete message and goodbye message
            expected_calls = [
                call("All questions have been reviewed. Session complete!"),
                call("Thank you, goodbye!")
            ]
            mock_print.assert_has_calls(expected_calls, any_order=False)

    def test_correct_answer_flow(self):
        """Test the flow when correct answers are given."""
        question_responses = ['Paris', 'q']  # First answer correct, then quit
        
        with patch('builtins.print') as mock_print, \
             patch('builtins.input', side_effect=question_responses):
            
            self.controller.start()
            
            # Verify correct feedback was printed
            mock_print.assert_any_call("Correct!")

    def test_incorrect_answer_flow(self):
        """Test the flow when incorrect answers are given."""
        question_responses = ['London', 'q']  # First answer wrong, then quit
        
        with patch('builtins.print') as mock_print, \
             patch('builtins.input', side_effect=question_responses):
            
            self.controller.start()
            
            # Verify incorrect feedback was printed
            calls = mock_print.call_args_list
            self.assertTrue(any('Incorrect' in str(call) for call in calls))

    def test_invalid_answer_flow(self):
        """Test handling of invalid answers."""
        # Start with a TrueFalse question
        questions = [{
            "type": "truefalse",
            "question": "Test question",
            "correct_answer": True
        }]
        controller = ARController(questions)
        
        with patch('builtins.print') as mock_print, \
             patch('builtins.input', side_effect=['invalid', 'q']):
            
            controller.start()
            mock_print.assert_any_call("Invalid input: Answer must be 'True' or 'False'.")

    def test_question_movement(self):
        """Test that questions move between boxes correctly during session."""
        responses = ['Paris', 'false', '4', 'q']  # Correct, Correct, Correct, then quit
        
        with patch('builtins.input', side_effect=responses), \
             patch('builtins.print'):
            
            self.controller.start()
            
            # Check if questions moved to correct boxes
            box_manager = self.controller._box_manager
            questions_in_box2 = len(box_manager._boxes[2]._questions)  # Correctly Answered Once
            self.assertGreater(questions_in_box2, 0)

    def test_empty_question_data(self):
        """Test initialization with empty question data."""
        controller = ARController([])
        with patch('builtins.print') as mock_print:
            controller.start()
            expected_calls = [
                call("All questions have been reviewed. Session complete!"),
                call("Thank you, goodbye!")
            ]
            mock_print.assert_has_calls(expected_calls, any_order=False)

if __name__ == '__main__':
    unittest.main()