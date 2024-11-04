#boxmanager.py

from .box import Box
from ars.qtype.question import Question
from datetime import timedelta
from typing import Dict, Optional

class BoxManager:

    def __init__(self):
        self._boxes = [
            Box("Missed Questions", timedelta(seconds=60)),
            Box("Unasked Questions", timedelta(seconds=0)),
            Box("Correctly Answered Once", timedelta(seconds=180)),
            Box("Correctly Answered Twice", timedelta(seconds=360)),
            Box("Known Questions", timedelta.max)
        ]
        self._question_location: Dict[str, int] = {}

    def add_new_question(self, question: Question) -> None:
        self._boxes[1].add_question(question)
        self._question_location[str(question.id)] = 1

    def move_question(self, question: Question, answered_correctly: bool) -> None:
        current_box_index = self._question_location[str(question.id)]
        new_box_index = (
            min(current_box_index + 1, 4) if answered_correctly else 0
        )
        self._boxes[current_box_index].remove_question(question)
        self._boxes[new_box_index].add_question(question)
        self._question_location[str(question.id)] = new_box_index
        self._log_box_counts()

    def get_next_question(self) -> Optional[Question]:
        for box in self._boxes[:-1]:  # Exclude the last box (Known Questions)
            question = box.get_next_priority_question()
            if question:
                return question
        return None

    def _log_box_counts(self) -> None:
        for box in self._boxes:
            print(f"{box.name}: {len(box)} questions")
