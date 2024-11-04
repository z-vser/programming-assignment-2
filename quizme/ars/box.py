#box.py

from ars.qtype.question import Question
from datetime import timedelta, datetime
from typing import List, Optional

class Box:


    def __init__(self, name: str, priority_interval: timedelta):
        self._name = name
        self._priority_interval = priority_interval
        self._questions: List[Question] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority_interval(self) -> timedelta:
        return self._priority_interval

    def add_question(self, question: Question) -> None:
        if question not in self._questions:
            self._questions.append(question)

    def remove_question(self, question: Question) -> None:
        if question in self._questions:
            self._questions.remove(question)

    def get_next_priority_question(self) -> Optional[Question]:
        now = datetime.now()
        for question in sorted(self._questions, key=lambda q: q.last_asked or datetime.min):
            if question.last_asked is None or (now - question.last_asked >= self._priority_interval):
                return question
        return None

    def __len__(self) -> int:
        return len(self._questions)

    def __str__(self) -> str:
        return f"Box(name='{self._name}', questions_count={len(self._questions)})"