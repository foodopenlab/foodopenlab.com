from enum import Enum


class MessagingChannel(str, Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    GMAIL = "gmail"
