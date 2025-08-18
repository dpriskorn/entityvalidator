from pydantic import BaseModel

from entityvalidator.enums import Necessity, PropertyResponse


class PropertyValue(BaseModel):
    name: str = ""
    necessity: Necessity
    response: PropertyResponse | None = None
