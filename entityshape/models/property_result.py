from typing import Any, Optional

from pydantic import BaseModel

from entityshape.enums import (
    Cardinality,
    Necessity,
    PropertyResponse,
    PropertyStatus,
    RequiredValueStatus,
    StatementResponse,
)


class PropertyResult(BaseModel):
    """Basic assumptions are
    Necessity.OPTIONAL
    StatementResponse.NOT_IN_SCHEMA
    """

    name: str = ""
    necessity: Necessity = Necessity.OPTIONAL
    cardinality: Cardinality = Cardinality.NONE
    property_status: PropertyStatus = PropertyStatus.NONE
    statement_response: StatementResponse = StatementResponse.NOT_IN_SCHEMA
    required_value_status: RequiredValueStatus = RequiredValueStatus.NONE
