from enum import Enum

class UserRole(str, Enum):
    GENERAL = "general"
    EXPERT  = "expert"
    ADMIN   = "admin"
