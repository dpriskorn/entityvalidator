from pydantic import BaseModel

from entityvalidator.enums import Necessity


class StatementValue(BaseModel):
    """
    Limitation:
    response can contain arbitrary strings with missing qualifiers so we cannot predict all possible values :/"""

    necessity: Necessity | None = None
    property: str = ""
    response: str
