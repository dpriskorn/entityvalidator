from typing import Optional

from pydantic import BaseModel

from entityshape.enums import Necessity, StatementResponse


class StatementValue(BaseModel):
    """
    Limitation:
    response can contain arbitrary strings with missing qualifiers so we cannot predict all possible values :/"""

    necessity: Optional[Necessity] = None
    property: str = ""
    response: str
