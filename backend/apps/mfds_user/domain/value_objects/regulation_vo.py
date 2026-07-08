from enum import Enum

class LawType(str, Enum):
    LAW = "law"          # 법령
    ADMRUL = "admrul"    # 행정규칙 (고시 등)
