import logging
from typing import Any, Dict, Set

from pydantic import BaseModel, ValidationError

from entityshape.enums import Necessity, PropertyResponse, StatementResponse
from entityshape.models.property_value import PropertyValue
from entityshape.models.statement_value import StatementValue

logger = logging.getLogger(__name__)


class Result(BaseModel):
    general: Dict[Any, Any] = {}
    name: str = ""
    properties: Dict[str, PropertyValue] = {}
    statements: Dict[Any, StatementValue] = {}
    missing_properties: Set[str] = set()
    required_properties: Set[str] = set()
    incorrect_statements: Set[str] = set()
    missing_statements: Set[str] = set()
    properties_with_too_many_statements: Set[str] = set()
    analyzed: bool = False
    required_properties_that_are_missing: Set[str] = set()
    optional_properties_that_are_missing: Set[str] = set()
    properties_without_enough_correct_statements: Set[str] = set()
    properties_that_are_not_allowed: Set[str] = set()
    statements_with_property_that_is_not_allowed: Set[str] = set()

    @property
    def some_required_properties_are_missing(self):
        return bool(self.required_properties_that_are_missing)

    @property
    def properties_with_too_many_statements_found(self):
        return bool(self.properties_with_too_many_statements)

    @property
    def incorrect_statements_found(self):
        return bool(self.incorrect_statements)

    @property
    def properties_without_enough_correct_statements_found(self):
        return bool(self.properties_without_enough_correct_statements)

    @property
    def statements_with_properties_that_are_not_allowed_found(self):
        return bool(self.statements_with_property_that_is_not_allowed)

    @property
    def is_valid(self) -> bool:
        """check if the properties are all allowed,
        all required properties are present,
        not too many statements,
        and none of the statements are incorrect"""
        self.analyze()
        return bool(
            not self.properties_with_too_many_statements_found
            and not self.incorrect_statements_found
            and not self.some_required_properties_are_missing
            and not self.properties_without_enough_correct_statements_found
            and not self.statements_with_properties_that_are_not_allowed_found
        )

    @property
    def is_empty(self):
        return bool(len(self.properties) == 0 and len(self.statements) == 0)

    def analyze(self):
        if not self.analyzed:
            self.__find_missing_properties__()
            self.__find_required_properties__()
            self.__find_incorrect_statements__()
            self.__find_properties_with_too_many_statements__()
            self.__find_properties_with_not_enough_correct_statements__()
            self.__find_required_properties_that_are_missing__()
            self.__find_optional_properties_that_are_missing__()
            self.__find_properties_that_are_not_allowed__()
            self.__find_statements_with_property_that_is_not_allowed__()
            self.analyzed = True

    def __find_properties_with_too_many_statements__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.TOO_MANY_STATEMENTS:
                self.properties_with_too_many_statements.add(property_)

    def __find_incorrect_statements__(self):
        for statement in self.statements:
            value: StatementValue = self.statements[statement]
            try:
                StatementResponse(value.response)
                if value.response == StatementResponse.INCORRECT:
                    self.incorrect_statements.add(statement)
            except ValueError:
                # Ignore responses we cannot predict
                logger.warning(f"Ignoring statement response: {value.response}")
                pass

    def __find_required_properties__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.necessity == Necessity.REQUIRED:
                self.required_properties.add(property_)

    def __find_missing_properties__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.MISSING:
                self.missing_properties.add(property_)

    def __find_required_properties_that_are_missing__(self):
        a = set(self.missing_properties)
        b = set(self.required_properties)
        # the intersection between these two should be empty
        # if all required properties are present
        self.required_properties_that_are_missing = a.intersection(b)

    def __find_optional_properties_that_are_missing__(self):
        """We calculate using set difference"""
        a = set(self.missing_properties)
        b = set(self.required_properties)
        self.optional_properties_that_are_missing = a.difference(b)

    def __find_properties_with_not_enough_correct_statements__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.NOT_ENOUGH_CORRECT_STATEMENTS:
                self.properties_without_enough_correct_statements.add(property_)

    def __find_properties_that_are_not_allowed__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.necessity == Necessity.ABSENT:
                self.properties_that_are_not_allowed.add(property_)

    def __find_statements_with_property_that_is_not_allowed__(self):
        for statement in self.statements:
            value: StatementValue = self.statements[statement]
            if value.necessity == Necessity.ABSENT:
                self.statements_with_property_that_is_not_allowed.add(value.property)
