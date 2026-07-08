from enum import Enum

class ExpertLabel(str, Enum):
    CORRECT   = "correct"
    PARTIAL   = "partial"
    INCORRECT = "incorrect"
