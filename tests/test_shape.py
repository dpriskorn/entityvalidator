from entityshape import Shape


class TestShape:
    def test_get_json_shape(self):
        s = Shape(eid="E375", lang="en")
        result = s.get_json_shape()
        # print(s.schema_text)
        assert result == {
            "P31": {
                "extra": "allowed",
                "allowed": ["Q2143825", "Q13405588"],
                "necessity": "optional",
                "status": "statement",
            },
            "P15": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P17": {
                "cardinality": {"min": 1},
                "necessity": "required",
                "status": "statement",
            },
            "P18": {"necessity": "optional", "status": "statement"},
            "P30": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P112": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P131": {
                "cardinality": {"min": 1},
                "necessity": "required",
                "status": "statement",
            },
            "P137": {"necessity": "optional", "status": "statement"},
            "P138": {"necessity": "optional", "status": "statement"},
            "P206": {"necessity": "optional", "status": "statement"},
            "P214": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P242": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P361": {"necessity": "optional", "status": "statement"},
            "P373": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P402": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P527": {"necessity": "optional", "status": "statement"},
            "P559": {"necessity": "optional", "status": "statement"},
            "P571": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P609": {"necessity": "optional", "status": "statement"},
            "P610": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P625": {
                "cardinality": {"max": 0, "min": 0},
                "necessity": "absent",
                "status": "statement",
            },
            "P646": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P691": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P706": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P856": {"necessity": "optional", "status": "statement"},
            "P910": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P973": {"necessity": "optional", "status": "statement"},
            "P1343": {"necessity": "optional", "status": "statement"},
            "P1427": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P1444": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P1545": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P1552": {
                "allowed": ["Q59421350"],
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P1589": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P1997": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P2043": {
                "cardinality": {"min": 1},
                "necessity": "required",
                "status": "statement",
            },
            "P2347": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P2671": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P2789": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P3018": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P3173": {"necessity": "optional", "status": "statement"},
            "P4552": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P6104": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P7127": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
            "P7252": {"necessity": "optional", "status": "statement"},
            "P10467": {
                "cardinality": {"min": 0, "max": 1},
                "necessity": "optional",
                "status": "statement",
            },
        }
        # console.print(result)
        # assert False

    # def test__translate_schema(self):
    #     raise AssertionError()
    #
    # def test__convert_shape(self):
    #     raise AssertionError()
    #
    # def test__assess_property(self):
    #     raise AssertionError()
    #
    # def test__get_shape_properties(self):
    #     raise AssertionError()
    #
    # def test__get_schema_json(self):
    #     raise AssertionError()
    #
    # def test__strip_schema_comments(self):
    #     raise AssertionError()
    #
    # def test__get_default_shape(self):
    #     raise AssertionError()
    #
    # def test__get_specific_shape(self):
    #     raise AssertionError()
    #
    # def test__find_parentheses(self):
    #     raise AssertionError()
    #
    # def test__translate_sub_shape(self):
    #     raise AssertionError()
    #
    # def test__get_cardinality(self):
    #     raise AssertionError()
    #
    # def test__get_snak_type(self):
    #     raise AssertionError()
    #
    # def test__assess_cardinality(self):
    #     raise AssertionError()
    #
    # def test__assess_sub_shape_key(self):
    #     raise AssertionError()
