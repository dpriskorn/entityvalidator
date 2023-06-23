from typing import List

from pydantic import BaseModel

from entityshape.enums import Extra, PropertyStatus, RequiredValueStatus


class Conditions(BaseModel):
    property_status: PropertyStatus = PropertyStatus.NONE
    extra: Extra = Extra.NONE
    missing_qualifiers: List[str] = []
    required_value_status: RequiredValueStatus = RequiredValueStatus.NONE
