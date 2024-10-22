import unittest
from datetime import timedelta, datetime
from unittest.mock import patch
from ars.boxmanager import BoxManager
from ars.qtype.shortanswer import ShortAnswer
from ars.qtype.truefalse import TrueFalse
from ars.box import Box

class TestBoxManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.manager = BoxManager()
        self.base_time = datetime(2024, 1, 1, 12, 0)
        
        # Create sample questions
        self.short_answer1 = ShortAnswer("What is the capital of France?", "Paris")
        self.short_answer2 = ShortAnswer("What is 2+2?", "4")
        self.true_false1 = TrueFalse("The Earth is flat", False, "The Earth is approximately spherical")
        self.true_false2 = TrueFalse("Python is a programming language", True, "Python is indeed a programming language")

    def test_initialization(self):
        """Test proper initialization of BoxManager."""
        # Should have 5 boxes
        self.assertEqual(len(self.manager._boxes), 5)
        
        # Verify box names and intervals
        expected_boxes = [
            ("Missed Questions", timedelta(seconds=60)),
            ("Unasked Questions", timedelta(seconds=0)),
            ("Correctly Answered Once", timedelta(seconds=180)),
            ("Correctly Answered Twice", timedelta(seconds=360)),
            ("Known Questions", timedelta.max)
        ]
        
        for i, (name, interval) in enumerate(expected_boxes):
            self.assertEqual(self.manager._boxes[i].name, name)
            self.assertEqual(self.manager._boxes[i].priority_interval, interval)

    def test_add_new_question(self):
        """Test adding new questions of different types."""
        # Add a ShortAnswer question
        self.manager.add_new_question(self.short_answer1)
        self.assertIn(self.short_answer1, self.manager._boxes[1]._questions)
        self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], 1)
        
        # Add a TrueFalse question
        self.manager.add_new_question(self.true_false1)
        self.assertIn(self.true_false1, self.manager._boxes[1]._questions)
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 1)

    def test_move_question_correct_answer(self):
        """Test moving questions when answered correctly."""
        self.manager.add_new_question(self.short_answer1)
        
        # Test progression through boxes with correct answers
        progression = [2, 3, 4, 4]  # Final 4 represents staying in Known Questions
        
        for expected_box in progression:
            self.manager.move_question(self.short_answer1, True)
            self.assertIn(self.short_answer1, self.manager._boxes[expected_box]._questions)
            self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], expected_box)

    def test_move_question_incorrect_answer(self):
        """Test moving questions when answered incorrectly."""
        self.manager.add_new_question(self.true_false1)
        
        # Move to box 2 first
        self.manager.move_question(self.true_false1, True)
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 2)
        
        # Now answer incorrectly
        self.manager.move_question(self.true_false1, False)
        self.assertIn(self.true_false1, self.manager._boxes[0]._questions)  # Should be in Missed Questions
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 0)

    def test_get_next_question_priority(self):
        """Test getting the next question based on priority."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.base_time
            
            # Add questions and set their last_asked times
            self.short_answer1._last_asked = self.base_time - timedelta(minutes=2)
            self.short_answer2._last_asked = self.base_time - timedelta(minutes=5)
            self.true_false1._last_asked = self.base_time
            
            self.manager.add_new_question(self.short_answer1)
            self.manager.add_new_question(self.short_answer2)
            self.manager.add_new_question(self.true_false1)
            
            # Move questions to different boxes
            self.manager.move_question(self.short_answer1, False)  # To Missed Questions
            self.manager.move_question(self.short_answer2, True)   # To Correctly Answered Once
            
            # Should get short_answer1 first (from Missed Questions)
            next_question = self.manager.get_next_question()
            self.assertEqual(next_question, self.short_answer1)

    def test_get_next_question_unasked(self):
        """Test that unasked questions are always returned regardless of last_asked time."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.base_time
            
            # Add a question with recent last_asked time
            self.true_false1._last_asked = self.base_time
            self.manager.add_new_question(self.true_false1)
            
            # Should still return the question because it's in Unasked Questions box
            next_question = self.manager.get_next_question()
            self.assertEqual(next_question, self.true_false1)

    def test_get_next_question_empty(self):
        """Test getting next question when no priority questions exist except in Known Questions."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.base_time
            
            # Add a question and move it to Known Questions box
            self.manager.add_new_question(self.short_answer1)
            
            # Move to Known Questions box
            for _ in range(3):
                self.manager.move_question(self.short_answer1, True)
                
            # Set recent last_asked time
            self.short_answer1._last_asked = self.base_time
            
            # Should return None since the question is in Known Questions
            # and no other questions exist
            self.assertIsNone(self.manager.get_next_question())

    def test_multiple_questions_same_box(self):
        """Test handling multiple questions in the same box."""
        questions = [
            self.short_answer1,
            self.short_answer2,
            self.true_false1,
            self.true_false2
        ]
        
        # Add all questions
        for q in questions:
            self.manager.add_new_question(q)
            
        # Verify all questions are in Unasked Questions box
        for q in questions:
            self.assertIn(q, self.manager._boxes[1]._questions)
            self.assertEqual(self.manager._question_location[str(q.id)], 1)
            
        # Move some questions
        self.manager.move_question(questions[0], True)  # To box 2
        self.manager.move_question(questions[1], False) # To box 0
        
        # Verify movements
        self.assertIn(questions[0], self.manager._boxes[2]._questions)
        self.assertIn(questions[1], self.manager._boxes[0]._questions)
        for q in questions[2:]:
            self.assertIn(q, self.manager._boxes[1]._questions)

    def test_box_transitions(self):
        """Test all possible box transitions with different question types."""
        # Test ShortAnswer transitions
        self.manager.add_new_question(self.short_answer1)
        
        self.manager.move_question(self.short_answer1, True)  # To Correctly Answered Once
        self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], 2)
        
        self.manager.move_question(self.short_answer1, True)  # To Correctly Answered Twice
        self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], 3)
        
        # Test TrueFalse transitions
        self.manager.add_new_question(self.true_false1)
        
        self.manager.move_question(self.true_false1, True)  # To Correctly Answered Once
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 2)
        
        self.manager.move_question(self.true_false1, False)  # To Missed Questions
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 0)

    def test_known_questions_behavior(self):
        """Test specific behavior for Known Questions box with both question types."""
        # Test with ShortAnswer
        self.manager.add_new_question(self.short_answer1)
        for _ in range(3):
            self.manager.move_question(self.short_answer1, True)
        self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], 4)
        
        # Test with TrueFalse
        self.manager.add_new_question(self.true_false1)
        for _ in range(3):
            self.manager.move_question(self.true_false1, True)
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 4)
        
        # Both should move to Missed Questions if answered incorrectly
        self.manager.move_question(self.short_answer1, False)
        self.manager.move_question(self.true_false1, False)
        self.assertEqual(self.manager._question_location[str(self.short_answer1.id)], 0)
        self.assertEqual(self.manager._question_location[str(self.true_false1.id)], 0)

if __name__ == '__main__':
    unittest.main()