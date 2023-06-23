from pydantic import BaseModel

from entityshape.exceptions import EidError, LangError, QidError
from entityshape.models.compareshape import CompareShape
from entityshape.models.result import Result
from entityshape.models.shape import Shape


class EntityShape(BaseModel):
    """This class models the entityshape API
    It has a default timeout of 10 seconds

    The API currently only support items"""

    qid = ""  # item
    eid = ""  # entityshape
    lang = ""  # language
    result: Result = Result()

    def __check__(self):
        if not self.lang:
            raise LangError("We only support 2 and 3 letter language codes")
        if not self.eid:
            raise EidError("We need an entityshape EID")
        if not self.qid:
            raise QidError("We need an item QID")

    def get_result(self) -> Result:
        """This method checks if we got the 3 parameters we need and
        gets the results and return them"""
        self.__check__()
        shape = Shape(eid=self.eid, lang=self.lang)
        comparison: CompareShape = CompareShape(
            shape=shape.get_json_shape(), qid=self.qid, lang=self.lang
        )
        comparison.compare()
        result = {
            "general": comparison.get_general(),
            "properties": comparison.get_properties(),
            "statements": comparison.get_statements(),
        }
        self.result = Result(**result)
        self.result.analyze()
        # print(self.result)
        return self.result

    # def check_lang(self):
    #     if not self.lang or 4 > len(self.lang) > 1:
    #         raise LangError("We only support 2 and 3 letter language codes")
    #
    # def check_eid(self):
    #     if not self.eid or :
    #         raise LangError("We only support 2 and 3 letter language codes")
