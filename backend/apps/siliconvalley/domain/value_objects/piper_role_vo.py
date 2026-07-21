from enum import Enum


class PiperRole(str, Enum):
    """Piper 크루의 역할 (실리콘밸리 조직 구성)."""

    CEO = "ceo"
    COO = "coo"
    HR = "hr"
    SYS = "sys"
    DASH = "dash"
