from unittest import TestCase

from entityshape import EidError, EntityShape, LangError, QidError, Result
from entityshape.exceptions import WikidataError


class TestEntityShape(TestCase):
    def test_get_result_invalid_eid(self):
        e = EntityShape(eid="eeeE1", lang="en", qid="Q1")
        with self.assertRaises(EidError):
            e.get_result()
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_lang(self):
        """The API does not seem to check whether the lang code is valid or not"""
        e = EntityShape(eid="E376", lang="eeeeen", qid="Q119853967")
        with self.assertRaises(LangError):
            e.get_result()
        assert e.result.is_valid is True
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_qid(self):
        e = EntityShape(eid="E1", lang="en", qid="qqqqQ1")
        with self.assertRaises(WikidataError):
            e.get_result()
        # print(e.result)
        # assert e.result != {}

    def test_get_result_valid(self):
        e = EntityShape(eid="E376", lang="en", qid="Q119853967")
        e.get_result()
        print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is True

    def test_get_result_invalid_wrong_schema(self):
        e = EntityShape(eid="E375", lang="en", qid="Q119853967")
        e.get_result()
        print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        assert e.result.required_properties_that_are_missing == {"P2043"}
        assert e.result.properties_that_are_not_allowed == {"P912", "P625", "P276"}
