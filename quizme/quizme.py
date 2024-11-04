import json
import argparse
from typing import List, Dict, Any
from ars.arcontroller import ARController

from pathlib import Path

def load_questions(file_path) -> List[Dict[str, Any]]:
    file_path = Path(file_path)  # Ensure file_path is treated as a Path object
    try:
        with file_path.open("r") as f:
            questions = json.load(f)
        return questions
    except FileNotFoundError:
        print(f"Error: Question file not found at {file_path}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in question file {file_path}")
        raise


def run_quiz(name: str, questions: List[Dict[str, Any]]) -> None:
    print(f"Welcome, {name}! Let's start your adaptive quiz session.")
    controller = ARController(questions)
    controller.start()

def main() -> None:
    parser = argparse.ArgumentParser(description="QuizMe: Adaptive Quiz CLI Application")
    parser.add_argument("name", type=str, help="Your name")
    parser.add_argument("--questions", type=Path, required=True, help="Path to the questions JSON file")
    args = parser.parse_args()

    try:
        questions = load_questions(args.questions)
        run_quiz(args.name, questions)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Exiting due to error in loading questions.")

if __name__ == "__main__":
    main()
