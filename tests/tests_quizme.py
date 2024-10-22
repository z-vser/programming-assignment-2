import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import json
from pathlib import Path
import argparse
from quizme import load_questions, run_quiz, main


class TestQuizMeCLI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.valid_json = '''[
            {
                "type": "shortanswer",
                "question": "What is the capital of France?",
                "correct_answer": "Paris"
            },
            {
                "type": "truefalse",
                "question": "The Earth is flat",
                "correct_answer": false,
                "explanation": "The Earth is approximately spherical"
            }
        ]'''
        
        self.parsed_questions = json.loads(self.valid_json)
        
    def test_load_questions_valid_file(self):
        """Test loading questions from a valid JSON file."""
        m = mock_open(read_data=self.valid_json)
        with patch('pathlib.Path.open', m):
            questions = load_questions(Path('test.json'))
            
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["question"], "What is the capital of France?")
        self.assertEqual(questions[1]["type"], "truefalse")

    def test_load_questions_file_not_found(self):
        """Test handling of missing question file."""
        m = mock_open()
        m.side_effect = FileNotFoundError
        
        with patch('pathlib.Path.open', m), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(FileNotFoundError):
                load_questions(Path('nonexistent.json'))
            
            mock_print.assert_called_with("Error: Question file not found at nonexistent.json")

    def test_load_questions_invalid_json(self):
        """Test handling of invalid JSON in question file."""
        invalid_json = '{invalid json'
        m = mock_open(read_data=invalid_json)
        
        with patch('pathlib.Path.open', m), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(json.JSONDecodeError):
                load_questions(Path('invalid.json'))
                
            mock_print.assert_called_with("Error: Invalid JSON in question file invalid.json")

    def test_run_quiz(self):
        """Test running the quiz with valid questions."""
        mock_controller = MagicMock()
        
        with patch('quizme.ARController', return_value=mock_controller) as mock_arc, \
             patch('builtins.print') as mock_print:
            
            run_quiz("Test User", self.parsed_questions)
            
            # Verify welcome message
            mock_print.assert_called_with("Welcome, Test User! Let's start your adaptive quiz session.")
            
            # Verify ARController usage
            mock_arc.assert_called_once_with(self.parsed_questions)
            mock_controller.start.assert_called_once()

    def test_main_successful_run(self):
        """Test successful execution of main function."""
        test_args = ['program', 'Test User', '--questions', 'questions.json']
        mock_args = argparse.Namespace(name='Test User', questions='questions.json')
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('quizme.load_questions', return_value=self.parsed_questions) as mock_load, \
             patch('quizme.run_quiz') as mock_run:
            
            main()
            
            # Verify questions were loaded
            mock_load.assert_called_once()
            
            # Verify quiz was run with correct arguments
            mock_run.assert_called_with('Test User', self.parsed_questions)

    def test_main_file_error(self):
        """Test main function handling of file loading error."""
        mock_args = argparse.Namespace(name='Test User', questions='nonexistent.json')
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('quizme.load_questions', side_effect=FileNotFoundError), \
             patch('builtins.print') as mock_print:
            
            main()
            
            # Verify error handling
            mock_print.assert_called_with("Exiting due to error in loading questions.")

    def test_argument_parsing(self):
        """Test command line argument parsing."""
        mock_args = argparse.Namespace(name='Test User', questions='questions.json')
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('quizme.load_questions', return_value=[]) as mock_load, \
             patch('quizme.run_quiz') as mock_run:
            
            main()
            
            # Verify quiz was run with correct name
            mock_run.assert_called_with('Test User', [])

    def test_missing_required_argument(self):
        """Test handling of missing required arguments."""
        mock_parser = MagicMock()
        mock_parser.parse_args.side_effect = SystemExit(2)
        
        with patch('argparse.ArgumentParser', return_value=mock_parser), \
             patch('sys.exit') as mock_exit:
            
            with self.assertRaises(SystemExit):
                main()

    def test_integration_flow(self):
        """Test the complete flow from argument parsing to quiz execution."""
        mock_args = argparse.Namespace(name='Test User', questions='questions.json')
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('pathlib.Path.open', mock_open(read_data=self.valid_json)), \
             patch('quizme.ARController') as mock_arc, \
             patch('builtins.print') as mock_print:
            
            mock_controller = MagicMock()
            mock_arc.return_value = mock_controller
            
            main()
            
            # Verify the complete flow
            expected_print_calls = [
                call("Welcome, Test User! Let's start your adaptive quiz session.")
            ]
            mock_print.assert_has_calls(expected_print_calls, any_order=False)
            mock_controller.start.assert_called_once()

if __name__ == '__main__':
    unittest.main()