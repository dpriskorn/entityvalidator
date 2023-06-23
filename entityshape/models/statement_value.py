from typing import Optional

from pydantic import BaseModel

from entityshape.enums import Necessity, StatementResponse


class StatementValue(BaseModel):
    necessity: Optional[Necessity] = None
    property: str = ""
    response: StatementResponse
