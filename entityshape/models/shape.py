"""
Copyright 2021 Mark Tully
Converts entityschema to json suitable for comparing with a wikidata item

2023: Dennis rewrote it to use Pydantic and added tests
"""
import os
import re
from typing import Any, Match, Optional, Pattern, Union

import requests
from pydantic import BaseModel


class Shape(BaseModel):
    """
    Produces a shape in the form of a json for a wikidata entityschema (e.g. E10)

    :param eid: The identifier of the entityschema to be processed
    :param lang: The language to get the schema name in

    :return name: the name of the entityschema
    :return shape: a json representation of the entityschema
    """

    eid: str
    lang: str
    property_line_regex = re.compile(r".+:P\d")
    property_select_regex = re.compile(r"P\d+")
    subshape_name_regex = re.compile(r"<.*>")
    cardinality_regex_one = re.compile(r"{.+}")
    cardinality_regex_two = re.compile(r"{((\d+)|(\d+,\d+))}")
    shape_names_regex = re.compile(r"\n<.*>")
    property_id_regex = re.compile(r"P\d+")
    schema_shape: dict = {}
    shapes: dict = {}
    schema_shapes: dict = {}
    default_shape_name: str = ""
    json_text: dict = {}
    raw_schema_text: str = ""
    schema_text_without_comments: str = ""
    schema_text: str = ""

    def get_json_shape(self):
        """
        Gets the json representation of the schema
        :return: the json representation of the schema
        """
        self._get_schema_json(self.eid)
        self._get_schema_text()
        self._remove_comments()
        self._strip_schema_text()
        if self.schema_text != "":
            self._get_default_shape()
            self._translate_schema()
        return self.schema_shape

    # def get_name(self):
    #     """
    #     Gets the name of the schema
    #     :return: the name of the schema
    #     """
    #     if self._language in self._json_text["labels"]:
    #         return self._json_text["labels"][self._language]
    #     return ""

    def _translate_schema(self):
        """
        Converts the entityschema to a json representation
        """
        for shape in self.shapes:
            self._convert_shape(shape)
        schema_json: dict = {}
        if self.default_shape_name != "":
            schema_json = self.schema_shapes[self.default_shape_name]
        for key in schema_json:
            if "shape" in schema_json[key]:
                schema_json[key] = self._translate_sub_shape(schema_json[key])
            if (
                "required" in schema_json[key]
                and "required" in schema_json[key]["required"]
            ):
                schema_json[key]["required"] = schema_json[key]["required"]["required"]
        self.schema_shape = schema_json

    def _convert_shape(self, shape: str):
        """
        Converts a shape into its json representation

        :param shape: the name of the shape to be converted
        """
        new_shape: str = self.shapes[shape].replace("\n", "")
        new_shape = new_shape.replace("\r", "")
        if "{" in new_shape:
            first_line = new_shape.split("{", 1)[0]
            shape_array: list = new_shape.split("{", 1)[1].split(";")
        else:
            first_line = new_shape.split("[", 1)[0]
            shape_array: list = new_shape.split("[", 1)[1].split(";")
        try:
            shape_json: dict = self._get_shape_properties(first_line)
        except AttributeError:
            shape_json: dict = {}
        for line in shape_array:
            if re.match(self.property_line_regex, line):
                child: dict = {}
                selected_property: str = re.search(
                    self.property_select_regex, line
                ).group(0)
                if shape_json.get(selected_property):
                    child = shape_json[selected_property]
                shape_json[selected_property] = self._assess_property(line, child)
            if "wikibase:lexicalCategory" in line:
                shape_json["lexicalCategory"] = self._assess_property(line, {})
            if "dct:language" in line:
                shape_json["language"] = self._assess_property(line, {})
        self.schema_shapes[shape] = shape_json

    def _assess_property(self, line: str, child: dict):
        """
        converts a line og a schema to a json representation of itself

        :param line: The line to be converted
        :param child: the existing json shape
        :return: a json object to be added to the shape
        """
        snak: str = self._get_snak_type(line)
        if "@<" in line:
            sub_shape_name: str = re.search(self.subshape_name_regex, line).group(0)
            child["shape"] = sub_shape_name[1:-1]
        if re.search(r"\[.*]", line):
            required_parameters_string: str = re.search(r"\[.*]", line).group(0)
            required_parameters_string = re.sub(r"wd:", "", required_parameters_string)
            if "^" in line:
                child["not_allowed"] = required_parameters_string[1:-1].split()
            else:
                child["allowed"] = required_parameters_string[1:-1].split()
        cardinality: dict = self._get_cardinality(line)
        necessity: str = "optional"
        if cardinality:
            necessity, child = self._assess_cardinality(necessity, child, cardinality)
        child["necessity"] = necessity
        child["status"] = snak
        return child

    def _get_shape_properties(self, first_line: str):
        """
        Get the overall properties of the shape

        :param first_line: The first line of the shape
        :return: a json representation of the properties of the first line
        """
        # a closed shape
        shape_json: dict = {}
        if "CLOSED" in first_line:
            shape_json = {"closed": "closed"}
        # a shape where values other than those specified are allowed for the specified properties
        if "EXTRA" in first_line:
            properties = re.findall(self.property_id_regex, first_line)
            for wikidata_property in properties:
                shape_json[wikidata_property] = {"extra": "allowed"}
        return shape_json

    def _get_schema_json(self, schema):
        """
        Downloads the schema from wikidata

        :param schema: the entityschema to be downloaded
        """
        url: str = f"https://www.wikidata.org/wiki/EntitySchema:{schema}?action=raw"
        response = requests.get(url)
        self.json_text = response.json()

    def _get_schema_text(self):
        self.raw_schema_text = self.json_text["schemaText"]

    def _remove_comments(self):
        # remove comments from the schema
        for line in self.raw_schema_text.splitlines():
            head, _, _ = line.partition("# ")
            if line.startswith("#"):
                head = ""
            self.schema_text_without_comments += f"\n{head.strip()}"

    def _strip_schema_text(self):
        """converts parts we don't care about
        because they're enforced by wikidata"""
        if self.schema_text_without_comments:
            self.schema_text = self.schema_text_without_comments
            # replace data types with the any value designator(.).  Since wikidata won't allow items
            # to enter the incorrect type (eg. trying to enter a LITERAL value where an IRI (i.e. a
            # wikidata item) is required will fail to save
            self.schema_text = self.schema_text.replace("IRI", ".")
            self.schema_text = self.schema_text.replace("LITERAL", ".")
            self.schema_text = self.schema_text.replace("xsd:dateTime", ".")
            self.schema_text = self.schema_text.replace("xsd:string", ".")
            self.schema_text = self.schema_text.replace("xsd:decimal", ".")
            self.schema_text = self.schema_text.replace(
                "[ <http://commons.wikimedia.org/wiki/Special:FilePath>~ ]", "."
            )
            self.schema_text = self.schema_text.replace(
                "[ <http://www.wikidata.org/entity>~ ]", "."
            )
            self.schema_text = os.linesep.join(
                [s for s in self.schema_text.splitlines() if s]
            )

    def _get_default_shape(self):
        """
        Gets the default shape to start at in the schema
        """
        default_shape_name: Optional[Match[str]] = re.search(
            r"start.*=.*@<.*>", self.schema_text, re.IGNORECASE
        )
        if default_shape_name is not None:
            default_name: str = default_shape_name.group(0).replace(" ", "")
            self.default_shape_name = default_name[8:-1]
            shape_names: list = re.findall(self.shape_names_regex, self.schema_text)
            for name in shape_names:
                self.shapes[name[2:-1]] = self._get_specific_shape(name[2:-1])

    def _get_specific_shape(self, shape_name: str):
        """
        Extracts a specific shape from the schema

        :param shape_name: The name of the shape to be extracted
        :return: The extracted shape
        """
        search: Union[Pattern[Union[str, Any]], Pattern] = re.compile(
            r"<%s>.*\n?([{\[])" % shape_name
        )
        parentheses = self._find_parentheses(self.schema_text)
        try:
            shape_index: int = re.search(search, self.schema_text).start()
        except AttributeError:
            shape_index = re.search("<%s>" % shape_name, self.schema_text).start()
        closest = None
        for character in parentheses:
            if (character >= shape_index) and (closest is None or character < closest):
                closest = character
        if closest:
            shape_start: int = shape_index
            shape_end: int = parentheses[closest]
            shape: str = self.schema_text[shape_start:shape_end]
            return shape
        return ""

    @staticmethod
    def _find_parentheses(shape):
        index_list = {}
        pop_stack = []
        for index, character in enumerate(shape):
            if character in ["{", "["]:
                pop_stack.append(index)
            elif character in ["}", "]"]:
                if len(pop_stack) == 0:
                    raise IndexError("Too many } for {")
                index_list[pop_stack.pop()] = index
        if len(pop_stack) > 0:
            raise IndexError("No matching } for {")
        return index_list

    def _translate_sub_shape(self, schema_json: dict):
        """
        Converts a sub-shape to a json representation

        :param schema_json: The json containing the shape to be extracted
        :return: The extracted shape
        """
        try:
            sub_shape: dict = self.schema_shapes[schema_json["shape"]]
            del schema_json["shape"]
        except KeyError:
            del schema_json["shape"]
            return schema_json
        qualifier_child: dict = {}
        reference_child: dict = {}
        for key in sub_shape:
            if "status" in sub_shape[key]:
                (
                    qualifier_child,
                    reference_child,
                    schema_json,
                ) = self._assess_sub_shape_key(
                    sub_shape, key, schema_json, qualifier_child, reference_child
                )
        schema_json["qualifiers"] = qualifier_child
        schema_json["references"] = reference_child
        return schema_json

    def _get_cardinality(self, schema_line: str):
        """
        Gets the cardinality of a line of the schema

        :param schema_line: The line to be processed
        :return: A json representation of the cardinality in the form {min:x, max:y}
        """
        cardinality: dict = {}
        if "?" in schema_line:
            cardinality["min"] = 0
            cardinality["max"] = 1
        elif "*" in schema_line:
            cardinality = {}
        elif "+" in schema_line:
            cardinality["min"] = 1
        elif "{0}" in schema_line:
            cardinality["max"] = 0
            cardinality["min"] = 0
        elif re.search(self.cardinality_regex_one, schema_line):
            match = re.search(self.cardinality_regex_two, schema_line)
            if hasattr(match, "group"):
                match = match.group()
                cardinalities = match[1:-1].split(",")
                cardinality["min"] = int(cardinalities[0])
                if len(cardinalities) == 1:
                    cardinality["max"] = int(cardinalities[0])
                else:
                    cardinality["max"] = int(cardinalities[1])
        else:
            cardinality["min"] = 1
            cardinality["max"] = 1
        return cardinality

    @staticmethod
    def _get_snak_type(schema_line: str):
        """
        Gets the type of snak from a schema line

        :param schema_line: The line to be processed
        :return: statement, qualifier or reference
        """
        if any(prop in schema_line for prop in ["wdt:", "ps:", "p:"]):
            return "statement"
        if "pq:" in schema_line:
            return "qualifier"
        return "reference"

    @staticmethod
    def _assess_cardinality(necessity: str, child: dict, cardinality: dict):
        if "cardinality" in child:
            if "min" in child["cardinality"] and "min" in cardinality:
                cardinality["min"] = cardinality["min"] + child["cardinality"]["min"]
            if "max" in child["cardinality"] and "max" in cardinality:
                cardinality["max"] = cardinality["max"] + child["cardinality"]["max"]
        child["cardinality"] = cardinality
        if "min" in cardinality and cardinality["min"] > 0:
            necessity = "required"
        if (
            "max" in cardinality
            and "min" in cardinality
            and cardinality["max"] == 0
            and cardinality["min"] == 0
        ):
            necessity = "absent"
        return necessity, child

    def _assess_sub_shape_key(
        self, sub_shape, key, schema_json, qualifier_child, reference_child
    ):
        if "shape" in key:
            sub_shape_json = self._translate_sub_shape(key)
            if key["status"] == "statement":
                schema_json["required"] = sub_shape_json
        if sub_shape[key]["status"] == "statement" and "allowed" in sub_shape[key]:
            value = sub_shape[key]["allowed"]
            schema_json["required"] = {key: value}
        if sub_shape[key]["status"] == "qualifier":
            qualifier_child[key] = sub_shape[key]
        if sub_shape[key]["status"] == "reference":
            reference_child[key] = sub_shape[key]
        return qualifier_child, reference_child, schema_json
