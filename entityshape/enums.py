from enum import Enum


class Necessity(Enum):
    ABSENT = "absent"
    OPTIONAL = "optional"
    REQUIRED = "required"


class PropertyResponse(Enum):
    MISSING = "missing"
    PRESENT = "present"
    INCORRECT = "incorrect"
    TOO_MANY_STATEMENTS = "too many statements"
    CORRECT = "correct"
    NOT_ENOUGH_CORRECT_STATEMENTS = "not enough correct statements"


class StatementResponse(Enum):
    NOT_IN_SCHEMA = "not in schema"
    ALLOWED = "allowed"
    INCORRECT = "incorrect"
    CORRECT = "correct"
    MISSING = "missing"
