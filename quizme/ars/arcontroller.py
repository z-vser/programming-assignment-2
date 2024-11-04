#arcontroller.py



from .boxmanager import BoxManager
from typing import List, Dict, Any
from .qtype.shortanswer import ShortAnswer
from .qtype.truefalse import TrueFalse


class ARController:
    def __init__(self, question_data: List[Dict[str, Any]]):
        self._box_manager = BoxManager()
        self._initialize_questions(question_data)

    def _initialize_questions(self, question_data: List[Dict[str, Any]]) -> None:
        for data in question_data:
            q_type = data.get("type")
            try:
                if q_type == "shortanswer":
                    question = ShortAnswer(data["question"], data["correct_answer"], data.get("case_sensitive", False))
                elif q_type == "truefalse":
                    question = TrueFalse(data["question"], data["correct_answer"], data.get("explanation", ""))
                else:
                    print(f"Unsupported question type: {q_type}. Skipping this question.")
                    continue
                self._box_manager.add_new_question(question)
            except KeyError as e:
                print(f"Missing required field for question: '{e.args[0]}'. Skipping this question.")
                continue
    def start(self) -> None:
        print("Starting quiz session. Type 'q' to quit at any time.")
        while True:
            question = self._box_manager.get_next_question()
            if not question:
                print("All questions have been reviewed. Session complete!")
                break

            print(question.ask())
            user_answer = input("Your answer: ")

            if user_answer.strip().lower() == "q":
                break

            try:
                correct = question.check_answer(user_answer)
                if correct:
                    print("Correct!")
                else:
                    print(question.incorrect_feedback())
                self._box_manager.move_question(question, correct)
            except ValueError as e:
                print(e)
        print("Thank you, goodbye!")
