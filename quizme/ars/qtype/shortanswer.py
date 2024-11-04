#shortanswer.py

from .question import Question
import re

class ShortAnswer(Question):

    def __init__(self, question: str, answer: str, case_sensitive: bool = False):
        super().__init__(question, answer)
        self._case_sensitive = case_sensitive

    def _normalize(self, text: str) -> str:
        text = text.strip()
        if not self._case_sensitive:
            text = text.lower()
        return re.sub(r'[^\w\s]', '', text)

    def check_answer(self, answer: str) -> bool:
        return self._normalize(answer) == self._normalize(self._answer)

    def incorrect_feedback(self) -> str:
        return f"Incorrect. The correct answer is: {self._answer}"
