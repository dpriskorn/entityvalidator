from typing import Optional

from pydantic import BaseModel

from entityshape.enums import Necessity, PropertyResponse


class PropertyValue(BaseModel):
    name: str = ""
    necessity: Necessity
    response: Optional[PropertyResponse] = None
