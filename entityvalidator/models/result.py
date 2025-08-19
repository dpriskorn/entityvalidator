import logging
from typing import Any

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator  # type: ignore

from entityvalidator.enums import Necessity, PropertyResponse, StatementResponse
from entityvalidator.models.property_value import PropertyValue
from entityvalidator.models.statement_value import StatementValue

logger = logging.getLogger(__name__)


class Result(BaseModel):
    general: dict[Any, Any] = {}
    name: str = ""
    properties: dict[str, PropertyValue] = {}
    statements: dict[Any, StatementValue] = {}
    missing_properties: set[str] = set()
    required_properties: set[str] = set()
    incorrect_statements: set[str] = set()
    missing_statements: set[str] = set()
    properties_with_too_many_statements: set[str] = set()
    analyzed: bool = False
    required_properties_that_are_missing: set[str] = set()
    optional_properties_that_are_missing: set[str] = set()
    properties_without_enough_correct_statements: set[str] = set()
    properties_that_are_not_allowed: set[str] = set()
    statements_with_property_that_is_not_allowed: set[str] = set()
    wikibase_url: str = "http://www.wikidata.org"
    mediawiki_api_url: str = "https://www.wikidata.org/w/api.php"

    @property
    def some_required_properties_are_missing(self) -> bool:
        return bool(self.required_properties_that_are_missing)

    @property
    def properties_with_too_many_statements_found(self) -> bool:
        return bool(self.properties_with_too_many_statements)

    @property
    def incorrect_statements_found(self) -> bool:
        return bool(self.incorrect_statements)

    @property
    def properties_without_enough_correct_statements_found(self) -> bool:
        return bool(self.properties_without_enough_correct_statements)

    @property
    def statements_with_properties_that_are_not_allowed_found(self) -> bool:
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
    def is_empty(self) -> bool:
        return bool(len(self.properties) == 0 and len(self.statements) == 0)

    def analyze(self) -> None:
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

    def __find_properties_with_too_many_statements__(self) -> None:
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.TOO_MANY_STATEMENTS:
                self.properties_with_too_many_statements.add(property_)

    def __find_incorrect_statements__(self) -> None:
        for statement in self.statements:
            value: StatementValue = self.statements[statement]
            try:
                StatementResponse(value.response)
                if value.response == StatementResponse.INCORRECT:
                    self.incorrect_statements.add(statement)
            except ValueError:
                # Ignore responses we cannot predict
                logger.warning(f"Ignoring statement response: {value.response}")

    def __find_required_properties__(self) -> None:
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.necessity == Necessity.REQUIRED:
                self.required_properties.add(property_)

    def __find_missing_properties__(self):
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.MISSING:
                self.missing_properties.add(property_)

    def __find_required_properties_that_are_missing__(self) -> None:
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

    def __find_properties_with_not_enough_correct_statements__(self) -> None:
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.response == PropertyResponse.NOT_ENOUGH_CORRECT_STATEMENTS:
                self.properties_without_enough_correct_statements.add(property_)

    def __find_properties_that_are_not_allowed__(self) -> None:
        for property_ in self.properties:
            value: PropertyValue = self.properties[property_]
            if value.necessity == Necessity.ABSENT:
                self.properties_that_are_not_allowed.add(property_)

    def __find_statements_with_property_that_is_not_allowed__(self) -> None:
        for statement in self.statements:
            value: StatementValue = self.statements[statement]
            if value.necessity == Necessity.ABSENT:
                self.statements_with_property_that_is_not_allowed.add(value.property)

    # def get_properties_as_a_string_with_labels_and_pid(
    #     self, wbi: WikibaseIntegrator, string_properties: Set[str]
    # ) -> str:
    #     properties: list[ResultProperty] = []
    #     for property_string in string_properties:
    #         wbi_property = wbi.property.get(property_string)
    #         property_object = ResultProperty(
    #             label=wbi_property.labels.get(language=self.lang).value,
    #             pid=property_string,
    #         )
    #         properties.append(property_object)
    #     return ", ".join([str(property_) for property_ in properties])

    # def __str__(self):
    #     return self.__repr__()
    #
    # def __repr__(self):
    #     """Return the result of the validation as a formatted string
    #     with output exactly describing what caused the validation to fail
    #
    #     We lookup the labels by default.
    #     If no language is set we fall back to English"""
    #     string = f"Valid: {self.is_valid}"
    #     if self.is_valid:
    #         return string
    #     else:
    #         from wikibaseintegrator.wbi_config import config as wbi_config  # type: ignore
    #
    #         # Update the WBI config with the values from the entityshape config
    #         # This enables support for any Wikibase
    #         wbi_config["MEDIAWIKI_API_URL"] = self.mediawiki_api_url
    #         wbi_config["WIKIBASE_URL"] = self.wikibase_url
    #         wbi = WikibaseIntegrator()
    #         if self.properties_with_too_many_statements_found:
    #             properties_string = self.get_properties_as_a_string_with_labels_and_pid(
    #                 string_properties=self.properties_with_too_many_statements, wbi=wbi
    #             )
    #             string += f"\nProperties with too many statements: {properties_string}"
    #         if self.properties_without_enough_correct_statements_found:
    #             properties_string = self.get_properties_as_a_string_with_labels_and_pid(
    #                 string_properties=self.properties_without_enough_correct_statements,
    #                 wbi=wbi,
    #             )
    #             string += (
    #                 f"\nProperties without enough correct statements: "
    #                 f"{properties_string}"
    #             )
    #         if self.required_properties_that_are_missing:
    #             properties_string = self.get_properties_as_a_string_with_labels_and_pid(
    #                 string_properties=self.required_properties_that_are_missing, wbi=wbi
    #             )
    #             string += f"\nRequired properties that are missing: {properties_string}"
    #         if self.incorrect_statements:
    #             string += f"\nIncorrect statements: {self.incorrect_statements}"
    #         return string

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict suitable for API responses."""
        return {
            # "name": self.name,
            # "general": self.general,
            # "lang": self.lang,
            # "wikibase_url": self.wikibase_url,
            # "mediawiki_api_url": self.mediawiki_api_url,
            "is_valid": self.is_valid,
            "is_empty": self.is_empty,
            "missing_properties": list(self.missing_properties),
            "required_properties": list(self.required_properties),
            "incorrect_statements": list(self.incorrect_statements),
            "missing_statements": list(self.missing_statements),
            "properties_with_too_many_statements": list(
                self.properties_with_too_many_statements
            ),
            "required_properties_that_are_missing": list(
                self.required_properties_that_are_missing
            ),
            "optional_properties_that_are_missing": list(
                self.optional_properties_that_are_missing
            ),
            "properties_without_enough_correct_statements": list(
                self.properties_without_enough_correct_statements
            ),
            # "properties_that_are_not_allowed": list(
            #     self.properties_that_are_not_allowed
            # ),
            "statements_with_property_that_is_not_allowed": list(
                self.statements_with_property_that_is_not_allowed
            ),
        }
