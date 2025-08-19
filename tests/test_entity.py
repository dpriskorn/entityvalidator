from unittest import TestCase

from entityvalidator import Entity, EntityIdError


class TestEntity(TestCase):
    def test_get_result_invalid_entity_id(self):
        e = Entity(
            eid="E1",
            entity_id="qqqqQ1",
            entity_data={},
            entity_schema_data={},
        )
        with self.assertRaises(EntityIdError):
            e.check_and_validate()
        # print(e.result)
        # assert e.result != {}
