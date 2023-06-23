from unittest import TestCase

from entityshape import ApiError, EidError, EntityShape, LangError, QidError, Result
from entityshape.models.compareshape import WikidataError


class TestEntityShape(TestCase):
    def test_get_result_invalid_eid(self):
        e = EntityShape(eid="eeeE1", lang="en", qid="Q1")
        with self.assertRaises(EidError):
            e.get_result()
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_lang(self):
        """The API does not seem to check whether the lang code is valid or not"""
        e = EntityShape(eid="E376", lang="", qid="Q119853967")
        with self.assertRaises(LangError):
            e.get_result()
        # assert e.result.is_valid is True
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_qid(self):
        e = EntityShape(eid="E1", lang="en", qid="qqqqQ1")
        with self.assertRaises(QidError):
            e.get_result()
        # print(e.result)
        # assert e.result != {}

    # TODO this fails because of ?
    # def test_get_result_valid(self):
    #     e = EntityShape(eid="E376", lang="en", qid="Q96308969")
    #     e.get_result()
    #     print(e.result)
    #     assert isinstance(e.result, Result)
    #     assert e.result.is_valid is True

    def test_get_result_invalid_missing_operator(self):
        e = EntityShape(eid="E376", lang="en", qid="Q96308969")
        e.get_result()
        print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        assert e.result.required_properties_that_are_missing == {"P137"}

    # this fails because of https://github.com/dpriskorn/entityshape/issues/2
    # def test_get_result_invalid_wrong_schema(self):
    #     e = EntityShape(eid="E375", lang="en", qid="Q119853967")
    #     e.get_result()
    #     print(e.result)
    #     assert isinstance(e.result, Result)
    #     assert e.result.is_valid is False
    #     assert e.result.required_properties_that_are_missing == {"P2043"}
    #     assert e.result.properties_that_are_not_allowed == {"P912", "P625", "P276"}
