"""
Copyright 2021 Mark Tully
Compares a json shape from shape.py with wikidata json
"""

import requests
from pydantic import BaseModel
from requests import Response

from entityshape.enums import Necessity, StatementResponse
from entityshape.exceptions import WikidataError
from entityshape.models.property_result import PropertyResult
from entityshape.models.propertyanalyzer import PropertyAnalyzer
from entityshape.models.shape_claim import ShapeClaim


class CompareShape(BaseModel):
    """
    Compares a wikidata entity (e.g. Q42) with a shape and returns the conformity of
    the statements and properties in the entity to the shape

    :param shape: The a json representation of the shape to be compared against
    :param qid: The entity to be compared (e.g. Q42)
    :param lang: The language to use for details like property names

    :returns properties: a json representation of the conformity of each property in the entity
    :returns statements: a json representation of the conformity of each statement in the entity
    """

    shape: dict
    qid: str
    lang: str
    property_responses: dict = {}
    properties: dict = {}
    entities: dict = {}
    raw_properties: list = []
    property_names: dict = {}
    claims: dict = {}
    statements: dict = {}

    def compare(self):

        self._get_entity_json()
        if self.entities["entities"][self.qid]:
            self._get_properties(self.entities["entities"][self.qid]["claims"])
        self._get_property_names(self.lang)
        # First we compare the statements
        self._get_claims()
        self._compare_statements()
        self._compare_properties()

    def get_properties(self) -> dict:
        """
        Gets the result of comparison for each property with the schema
        :return: json for comparison of properties
        """
        return self._compare_properties()

    def get_statements(self) -> dict:
        """
        Gets the result of comparison of each statement with the schema
        :return: json for comparison of statements
        """
        return self._compare_statements()

    def get_general(self) -> dict:
        """
        Gets general properties of the comparison
        :return: json for general properties of the comparison
        """
        general: dict = {}
        properties: list = ["lexicalCategory", "language"]
        for item in properties:
            if item in self.shape and item in self.entities["entities"][self.qid]:
                expected: list = self.shape[item]["allowed"]
                actual: str = self.entities["entities"][self.qid][item]
                general[item] = "incorrect"
                if actual in expected:
                    general[item] = "correct"
        return general

    def _get_claims(self):
        self.claims: dict = self.entities["entities"][self.qid]["claims"]
        # console.print(claims)
        # sys.exit()

    def _compare_statements(self):
        """
        Compares the statements in the entity to the schema
        """
        # TODO avoid passing variables around and use pydantic instead
        # iterate through the raw claims from Wikidata
        # the property_id is the key and the value is an array
        # 'P31': [
        #         {
        #             'mainsnak': {
        #                 'snaktype': 'value',
        #                 'property': 'P31',
        #                 'hash': 'e31711f94aca8f3398eff096eaf875da8ba16d20',
        #                 'datavalue': {
        #                     'value': {
        #                         'entity-type': 'item',
        #                         'numeric-id': 96650551,
        #                         'id': 'Q96650551'
        #                     },
        #                     'type': 'wikibase-entityid'
        #                 },
        #                 'datatype': 'wikibase-item'
        #             },
        #             'type': 'statement',
        #             'id': 'Q119853967$D8462BF0-2599-4F62-8147-E84465529B19',
        #             'rank': 'normal'
        #         }
        #     ],
        for property_id in self.claims:
            self.analyze_property_statements(property_id=property_id)

    def analyze_property_statements(self, property_id):
        """We analyze the statements of the property"""
        # result variables
        statement_results: list = []
        property_statement_results: list = []
        # iterate through the statements on each claim
        for statement in self.claims[property_id]:
            #         {
            #             'mainsnak': {
            #                 'snaktype': 'value',
            #                 'property': 'P31',
            #                 'hash': 'e31711f94aca8f3398eff096eaf875da8ba16d20',
            #                 'datavalue': {
            #                     'value': {
            #                         'entity-type': 'item',
            #                         'numeric-id': 96650551,
            #                         'id': 'Q96650551'
            #                     },
            #                     'type': 'wikibase-entityid'
            #                 },
            #                 'datatype': 'wikibase-item'
            #             },
            #             'type': 'statement',
            #             'id': 'Q119853967$D8462BF0-2599-4F62-8147-E84465529B19',
            #             'rank': 'normal'
            #         }

            property_result = PropertyResult(
                property_id=property_id,
            )
            if property_id in self.shape:
                # It is in the schema :)
                shape_claim = ShapeClaim(
                    property_id=property_id,
                    statement=statement,
                    property_value=property_result,
                    shape=self.shape,
                )
                conditions = shape_claim.get_conditions_from_shape()
                conditions = shape_claim.process_allowed(conditions)
                # Carry over the results
                property_result.property_status = conditions.property_status
                property_result.required_ = conditions.required_value_status
                property_result.statement_response = ??
            self.statements[statement["id"]] = property_result
            statement_results.append(statement_response)
            # TODO rewrite to OOP and enums
            # if statement_response.startswith("missing"):
            #     statement_response = "incorrect"
            property_statement_results.append(statement_response)
        self.property_responses[property_id] = property_statement_results

    def _compare_properties(self):
        """
        Compares the properties in the entity to the schema
        """
        for property_id in self.raw_properties:
            # Basic assumption that the response is missing and necessity=absent
            property_value = PropertyResult(
                name=self.property_names[property_id],
            )
            # Update the necessity
            if property_id in self.shape and "necessity" in self.shape[property_id]:
                property_value.necessity = Necessity(
                    self.shape[property_id]["necessity"]
                )
            if property_id in self.entities["entities"][self.qid]["claims"]:
                pa = PropertyAnalyzer(
                    property_id=property_id,
                    property_value=property_value,  # this is needed for the cardinality check
                    property_responses=self.property_responses,
                    shape=self.shape,
                )
                pa.analyze()
                # Propagate results
                property_value.property_status = pa.property_status
                property_value.cardinality = pa.cardinality
            self.properties[property_id] = property_value
        return self.properties

    def _get_entity_json(self):
        """
        Downloads the entity from wikidata
        """
        url: str = f"https://www.wikidata.org/wiki/Special:EntityData/{self.qid}.json"
        response: Response = requests.get(url)
        if response.status_code == 200:
            self.entities = response.json()
        else:
            raise WikidataError(f"Got {response.status_code} from Wikidata for {url}")

    def _get_properties(self, claims: dict):
        """
        Gets a list of properties included in the entity
        :param claims: The claims in the entity
        """
        for claim in claims:
            if claim not in self.raw_properties:
                self.raw_properties.append(claim)
        for claim in self.shape:
            if claim not in self.raw_properties and claim.startswith("P"):
                self.raw_properties.append(claim)

    def _get_property_names(self, language: str):
        """
        Gets the names of properties from wikidata
        """
        wikidata_property_list: list = [
            self.raw_properties[i * 49 : (i + 1) * 49]
            for i in range((len(self.raw_properties) + 48) // 48)
        ]
        for element in wikidata_property_list:
            required_properties: str = "|".join(element)
            url: str = (
                f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids="
                f"{required_properties}&props=labels&languages={language}&format=json"
            )
            response: Response = requests.get(url)
            if response.status_code == 200:
                json_text: dict = response.json()
            else:
                raise WikidataError(
                    f"Got {response.status_code} from Wikidata for {url}"
                )
            for item in element:
                try:
                    self.property_names[json_text["entities"][item]["id"]] = json_text[
                        "entities"
                    ][item]["labels"][language]["value"]
                except KeyError:
                    self.property_names[json_text["entities"][item]["id"]] = ""
