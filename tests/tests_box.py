import unittest
from datetime import datetime, timedelta
from ars.box import Box
from ars.qtype.question import Question
from unittest.mock import patch 



class MockQuestion(Question):
    """Mock Question class for testing."""
    def __init__(self, question: str, answer: str, last_asked: datetime = None):
        super().__init__(question, answer)
        if last_asked:
            self._last_asked = last_asked
            
    def check_answer(self, answer: str) -> bool:
        return True  # Simplified for testing
        
    def incorrect_feedback(self) -> str:
        return "Incorrect"  # Simplified for testing

class TestBox(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.box_name = "Test Box"
        self.priority_interval = timedelta(days=1)
        self.box = Box(self.box_name, self.priority_interval)
        self.base_time = datetime(2024, 1, 1, 12, 0)  # Fixed time for testing
        
        # Create some test questions
        self.question1 = MockQuestion("Q1", "A1", self.base_time - timedelta(days=2))
        self.question2 = MockQuestion("Q2", "A2", self.base_time - timedelta(hours=12))
        self.question3 = MockQuestion("Q3", "A3", self.base_time - timedelta(days=1))

    def test_initialization(self):
        """Test box initialization."""
        self.assertEqual(self.box.name, self.box_name)
        self.assertEqual(self.box.priority_interval, self.priority_interval)
        self.assertEqual(len(self.box), 0)
        self.assertEqual(str(self.box), f"Box(name='{self.box_name}', questions_count=0)")

    def test_add_question(self):
        """Test adding questions to the box."""
        # Test adding a single question
        self.box.add_question(self.question1)
        self.assertEqual(len(self.box), 1)
        
        # Test adding duplicate question
        self.box.add_question(self.question1)
        self.assertEqual(len(self.box), 1)
        
        # Test adding multiple different questions
        self.box.add_question(self.question2)
        self.box.add_question(self.question3)
        self.assertEqual(len(self.box), 3)

    def test_remove_question(self):
        """Test removing questions from the box."""
        # Add questions first
        self.box.add_question(self.question1)
        self.box.add_question(self.question2)
        
        # Test removing existing question
        self.box.remove_question(self.question1)
        self.assertEqual(len(self.box), 1)
        
        # Test removing non-existent question
        self.box.remove_question(self.question3)
        self.assertEqual(len(self.box), 1)
        
        # Test removing last question
        self.box.remove_question(self.question2)
        self.assertEqual(len(self.box), 0)

    def test_get_next_priority_question(self):
        """Test retrieving priority questions."""
        # Add questions with different last_asked times
        self.box.add_question(self.question1)  # 2 days ago
        self.box.add_question(self.question2)  # 12 hours ago
        self.box.add_question(self.question3)  # 1 day ago
        
        # Test with current time
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.base_time
            
            # Should return question1 (oldest)
            next_question = self.box.get_next_priority_question()
            self.assertEqual(next_question, self.question1)
            
            # Remove question1 and test again
            self.box.remove_question(self.question1)
            next_question = self.box.get_next_priority_question()
            self.assertEqual(next_question, self.question3)  # Next oldest eligible question

    def test_no_priority_questions(self):
        """Test behavior when no priority questions are available."""
        # Add a recently asked question
        recent_question = MockQuestion("Recent", "Answer", datetime.now() - timedelta(minutes=30))
        self.box.add_question(recent_question)
        
        # Should return None as no questions meet priority interval
        self.assertIsNone(self.box.get_next_priority_question())

    def test_box_properties(self):
        """Test box property getters."""
        self.assertEqual(self.box.name, self.box_name)
        self.assertEqual(self.box.priority_interval, self.priority_interval)

    def test_box_string_representation(self):
        """Test string representation of box."""
        self.box.add_question(self.question1)
        self.box.add_question(self.question2)
        expected_str = f"Box(name='{self.box_name}', questions_count=2)"
        self.assertEqual(str(self.box), expected_str)

    def test_edge_cases(self):
        """Test edge cases."""
        # Test with empty string name
        empty_box = Box("", timedelta(days=1))
        self.assertEqual(empty_box.name, "")
        
        # Test with zero priority interval
        zero_interval_box = Box("Zero", timedelta(0))
        self.assertEqual(zero_interval_box.priority_interval, timedelta(0))
        
        # Test with very large priority interval
        large_interval = timedelta(days=365*100)  # 100 years
        large_interval_box = Box("Large", large_interval)
        self.assertEqual(large_interval_box.priority_interval, large_interval)
        
        # Test with very short priority interval
        short_interval_box = Box("Short", timedelta(microseconds=1))
        self.assertEqual(short_interval_box.priority_interval, timedelta(microseconds=1))

    def test_priority_sorting(self):
        """Test that questions are properly sorted by last_asked time."""
        # Create questions with specific last_asked times
        q1 = MockQuestion("Q1", "A1", self.base_time - timedelta(days=3))
        q2 = MockQuestion("Q2", "A2", self.base_time - timedelta(days=2))
        q3 = MockQuestion("Q3", "A3", self.base_time - timedelta(days=1))
        
        # Add questions in random order
        self.box.add_question(q2)
        self.box.add_question(q3)
        self.box.add_question(q1)
        
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = self.base_time
            
            # Should return oldest question first
            self.assertEqual(self.box.get_next_priority_question(), q1)
            
            self.box.remove_question(q1)
            self.assertEqual(self.box.get_next_priority_question(), q2)
            
            self.box.remove_question(q2)
            self.assertEqual(self.box.get_next_priority_question(), q3)

if __name__ == '__main__':
    unittest.main()