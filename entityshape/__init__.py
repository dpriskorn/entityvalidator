import re
from typing import Any, Dict, Optional

from pydantic import BaseModel

from entityshape.exceptions import ApiError, EidError, LangError, QidError
from entityshape.models.compareshape import CompareShape
from entityshape.models.result import Result
from entityshape.models.shape import Shape


class EntityShape(BaseModel):
    """This class models the entityshape API
    It has a default timeout of 10 seconds

    The API currently only support items"""

    entity_id: str = ""  # item or lexeme
    eid: str = ""  # entityshape
    lang: str = "en"  # language defaults to English
    result: Result = Result()
    eid_regex = re.compile(r"E\d+")
    entity_id_regex = re.compile(r"[QL]\d+")
    compare_shape_result: Optional[Dict[str, Any]] = None

    def __check_inputs__(self):
        if not self.lang:
            raise LangError("We only support 2 and 3 letter language codes")
        if not self.eid:
            raise EidError("We need an entityshape EID")
        if not re.match(self.eid_regex, self.eid):
            raise EidError("EID has to be E followed by only numbers like this: E100")
        if not self.entity_id:
            raise QidError("We need an item QID")
        if not re.match(self.entity_id_regex, self.entity_id):
            raise QidError("QID has to be Q followed by only numbers like this: Q100")

    def validate_and_get_result(self) -> Result:
        """This method checks if we got the 3 parameters we need and
        gets the results and return them"""
        self.__check_inputs__()
        self.__validate__()
        return self.__parse_result__()

    def __validate__(self):
        shape: Shape = Shape(self.eid, self.lang)
        comparison: CompareShape = CompareShape(
            shape.get_schema_shape(), self.entity_id, self.lang
        )
        self.compare_shape_result = {}
        self.compare_shape_result = {
            "general": comparison.get_general(),
            "properties": comparison.get_properties(),
            "statements": comparison.get_statements(),
        }

    def __parse_result__(self) -> Result:
        if self.compare_shape_result:
            self.result = Result(**self.compare_shape_result)
            self.result.lang = self.lang
            self.result.analyze()
            return self.result
        else:
            return Result()
