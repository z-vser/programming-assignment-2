#question.py

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

class Question(ABC):
   

    def __init__(self, question: str, answer: Any):
        self._id = uuid.uuid4()
        self._question = question
        self._answer = answer
        self._last_asked = None

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def last_asked(self) -> Optional[datetime]:
        return self._last_asked

    def ask(self) -> str:
        self._last_asked = datetime.now()
        return self._question

    def reset(self) -> None:
        self._last_asked = None

    @abstractmethod
    def check_answer(self, answer: Any) -> bool:
        pass

    @abstractmethod
    def incorrect_feedback(self) -> str:
        pass

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Question) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"Question(id={self.id}, question={self._question})"
