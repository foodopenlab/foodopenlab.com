from enum import Enum


class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    SETTLEMENT = "settlement"
