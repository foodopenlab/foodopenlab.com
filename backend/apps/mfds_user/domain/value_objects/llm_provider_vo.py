from enum import Enum

class LLMProvider(str, Enum):
    GEMINI     = "gemini"
    API_GEMINI = "api+gemini"
