from unittest import TestCase

# from rich.console import Console
from entityshape import EidError, EntityShape, LangError, QidError, Result


class TestEntityShape(TestCase):
    def test_get_result_invalid_eid(self):
        e = EntityShape(eid="eeeE1", lang="en", entity_id="Q1")
        with self.assertRaises(EidError):
            e.validate_and_get_result()
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_lang(self):
        """The API does not seem to check whether the lang code is valid or not"""
        e = EntityShape(eid="E376", lang="", entity_id="Q119853967")
        with self.assertRaises(LangError):
            e.validate_and_get_result()
        # assert e.result.is_valid is True
        # print(e.result)
        # assert e.result != {}

    def test_get_result_invalid_entity_id(self):
        e = EntityShape(eid="E1", lang="en", entity_id="qqqqQ1")
        with self.assertRaises(QidError):
            e.validate_and_get_result()
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
        e = EntityShape(eid="E376", lang="en", entity_id="Q96308969")
        e.validate_and_get_result()
        # print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        assert e.result.required_properties_that_are_missing == {"P137"}

    # this fails because of https://github.com/dpriskorn/entityshape/issues/2
    # def test_get_result_invalid_wrong_schema(self):
    #     e = EntityShape(eid="E375", lang="en", entity_id="Q119853967")
    #     e.get_result()
    #     print(e.result)
    #     assert isinstance(e.result, Result)
    #     assert e.result.is_valid is False
    #     assert e.result.required_properties_that_are_missing == {"P2043"}
    #     assert e.result.properties_that_are_not_allowed == {"P912", "P625", "P276"}

    def test_get_result_missing_statement_response(self):
        e = EntityShape(eid="E395", lang="en", entity_id="Q4802448")
        e.validate_and_get_result()
        # print(e.compare_shape_result)
        # console = Console()
        # console.print(e.result)
        assert isinstance(e.result, Result)
        assert e.result.is_valid is False
        assert e.result.properties_without_enough_correct_statements == {"P39"}

    def test_get_result_weird_statement_response_party_person(self):
        e = EntityShape(eid="E395", lang="en", entity_id="Q20727")
        e.validate_and_get_result()
        assert isinstance(e.result, Result)
        assert e.result.is_valid is True

    def test_lexeme(self):
        # wbi_config['USER_AGENT'] = 'WikibaseIntegrator in PAWS by So9q'
        # wbi = WikibaseIntegrator()
        # # This query was build in a few seconds using https://query.wikidata.org/querybuilder/?uselang=en :)
        # results = execute_sparql_query("""
        # SELECT ?lexemeId ?lemma WHERE {
        #   ?lexemeId dct:language wd:Q9027;
        #             wikibase:lexicalCategory wd:Q1084;
        #             wikibase:lemma ?lemma.
        # }
        # limit 10
        # """)
        # bindings = results["results"]["bindings"]
        # print(f"Found {len(bindings)} results")
        # count = 1
        # for result in bindings:
        #     print(result)
        #     # Get the entity id from the URI
        #     entity_id = result["lexemeId"]["value"].split("/")[-1]
        #     print(f"Working on: {entity_id}")
        #     entity = wbi.lexeme.get(entity_id)
        e = EntityShape(entity_id="L41172", eid="E34", lang="en")
        e.validate_and_get_result()
        print(e.result)
        # try:
        #     result = e.validate_and_get_result()
        #     # Ignore the invalid shelters missing an operator P137
        #     if result.is_valid is False and result.required_properties_that_are_missing == {"P137"}:
        #         print("Skipping item only missing an operator")
        #     # Ignore the invalid items with too many P625
        #     elif result.is_valid is False and result.properties_with_too_many_statements == {"P625"}:
        #         print("Skipping item that only invalidates because it has a coordinate")
        #     elif result.is_valid is True:
        #         print("Skipping valid item - they are boring!")
        #     else:
        #         print(repr(result) + f"\nSee {entity.get_entity_url()}")
        # except KeyError:
        #     print(
        #         f"Got a keyerror for the entity {entity_id}, this is a known bug with entityshape, see https://github.com/dpriskorn/entityshape/issues/2")
