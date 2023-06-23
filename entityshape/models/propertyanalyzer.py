from typing import Optional

from pydantic import BaseModel

from entityshape.enums import Cardinality, Necessity, PropertyResponse, PropertyStatus
from entityshape.models.property_value import PropertyResult


class PropertyAnalyzer(BaseModel):
    """We analyze if the property is allowed or not and if the cardinality is correct"""

    property_id: str
    property_value: PropertyResult
    property_responses: dict
    shape: dict
    cardinality: Cardinality = Cardinality.NONE
    property_status: PropertyStatus = PropertyStatus.NONE
    present: bool = True

    def analyze(self):
        self._assess_cardinality()
        # These are based on the earlier analysis of the statements
        if "incorrect" in self.property_responses[self.property_id]:
            self.property_status = PropertyStatus.INCORRECT
        elif "correct" in self.property_responses[self.property_id]:
            self.property_status = PropertyStatus.CORRECT

    def _assess_cardinality(self):
        if self.property_id in self.shape:
            number_of_statements: int = len(self.property_responses[self.property_id])
            min_cardinality = False
            max_cardinality = False
            # We assume it is correct unless it should be absent
            if self.property_value.necessity != Necessity.ABSENT:
                self.cardinality = Cardinality.CORRECT
            # Check if min/max cardinality is correct
            if "cardinality" in self.shape[self.property_id]:
                claim_cardinality = self.shape[self.property_id]["cardinality"]
                min_cardinality = True
                max_cardinality = True
                if "extra" in self.shape[self.property_id]:
                    number_of_statements = self.property_responses[
                        self.property_id
                    ].count("correct")
                if (
                    "min" in claim_cardinality
                    and number_of_statements < claim_cardinality["min"]
                ):
                    min_cardinality = False
                if (
                    "max" in claim_cardinality
                    and number_of_statements > claim_cardinality["max"]
                ):
                    max_cardinality = False
            if min_cardinality and not max_cardinality:
                self.cardinality = Cardinality.TOO_MANY_STATEMENTS
            if max_cardinality and not min_cardinality:
                self.cardinality = Cardinality.NOT_ENOUGH_CORRECT_STATEMENTS
