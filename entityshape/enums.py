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
    NONE = ""


class StatementResponse(Enum):
    NOT_IN_SCHEMA = "not in schema"
    ALLOWED = "allowed"
    INCORRECT = "incorrect"
    CORRECT = "correct"


class Extra(Enum):
    EXTRA = "extra"
    NONE = ""


class RequiredValueStatus(Enum):
    MISSING = "missing"
    PRESENT = "present"
    INCORRECT = "incorrect"
    NONE = ""


class PropertyStatus(Enum):
    NONE = ""
    ALLOWED = "allowed"
    NOT_ALLOWED = "not allowed"
    INCORRECT = "incorrect"
    CORRECT = "correct"


class Cardinality(Enum):
    CORRECT = "correct"
    TOO_MANY_STATEMENTS = "too many statements"
    NOT_ENOUGH_CORRECT_STATEMENTS = "not enough correct statements"
    NONE = ""
