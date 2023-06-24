from unittest import TestCase

# from rich.console import Console
from entityshape import EidError, EntityShape, LangError, QidError, Result


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

    def test_get_result_missing_statement_response(self):
        e = EntityShape(eid="E395", lang="en", qid="Q4802448")
        e.get_result()
        # print(e.compare_shape_result)
        # console = Console()
        # console.print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        assert e.result.properties_without_enough_correct_statements == {"P39"}

    def test_get_result_weird_statement_response_party_person(self):
        e = EntityShape(eid="E395", lang="en", qid="Q20727")
        e.get_result()
        # print(e.compare_shape_result)
        # console = Console()
        # console.print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        # assert e.result.properties_without_enough_correct_statements == {"P39"}
