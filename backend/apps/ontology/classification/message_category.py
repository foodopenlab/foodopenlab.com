from enum import Enum


class MessageCategory(str, Enum):
    SPAM = "spam"
    LEGIT = "legit"
    PHISHING = "phishing"
    AD = "ad"
