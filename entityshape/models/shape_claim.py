import requests
from pydantic import BaseModel
from requests import Response

from entityshape.enums import Extra, PropertyStatus, RequiredValueStatus
from entityshape.exceptions import WikidataError
from entityshape.models.conditions import Conditions


class ShapeClaim(BaseModel):
    property_id: str
    statement: dict
    property_value: dict
    shape: dict
    conditions: Conditions = Conditions()
    allowed_qualifiers: list = []

    @property
    def shape_claim(self):
        return self.shape[self.property_id]

    def get_conditions_from_shape(self) -> Conditions:
        # TODO rewrite to support somevalue and novalue
        mainsnak = self.statement["mainsnak"]
        # This if is neccessary for EntityShape(eid="E376", lang="en", qid="Q119853967") because it contains a "somevalue"
        # if "datavalue" in mainsnak:
        datavalue: dict = mainsnak["datavalue"]
        self.conditions.property_status = PropertyStatus.PRESENT
        if "necessity" in self.shape_claim:
            self.property_value["necessity"] = self.shape_claim["necessity"]
            self.conditions.property_status = PropertyStatus.ALLOWED
        if "allowed" in self.shape_claim:
            self.conditions.property_status = self._process_allowed_in_shape_claim(
                self.property_id, datavalue
            )
        if "not_allowed" in self.shape_claim and "id" in datavalue["value"]:
            value: str = datavalue["value"]["id"]
            if value in self.shape_claim["not_allowed"]:
                self.conditions.property_status = PropertyStatus.NOT_ALLOWED
        if "extra" in self.shape_claim:
            self.conditions.extra = Extra.EXTRA
        if "qualifiers" in self.shape_claim:
            self.conditions.missing_qualifiers = (
                self._process_qualifiers_in_shape_claim()
            )
        if "required" in self.shape_claim:
            self.conditions.required_value_status = (
                self._process_required_value_in_shape_claim(datavalue)
            )
        self.process_allowed()

    def _process_allowed_in_shape_claim(self, claim, param) -> PropertyStatus:
        # TODO avoid passing variables around and use pydantic instead
        allowed = PropertyStatus.CORRECT
        if "id" in param["value"]:
            value: str = param["value"]["id"]
            if value not in self.shape[claim]["allowed"]:
                allowed = PropertyStatus.INCORRECT
        return allowed

    def _process_required_value_in_shape_claim(self, datavalue) -> RequiredValueStatus:
        # TODO avoid passing variables around and use pydantic instead
        required_value_status: RequiredValueStatus = RequiredValueStatus.NONE
        if "required" in self.shape_claim["required"]:
            shape_claim_required = self.shape_claim["required"]["required"]
            required_property: str = list(shape_claim_required.keys())[0]
            required_value: str = shape_claim_required[required_property][0]
        else:
            required_property: str = list(self.shape_claim["required"].keys())[0]
            required_value: str = self.shape_claim["required"][required_property][0]

        query_entity: str = datavalue["value"]["id"]
        url: str = (
            f"https://www.wikidata.org/w/api.php?action=wbgetclaims"
            f"&entity={query_entity}&property={required_property}&format=json"
        )
        response: Response = requests.get(url)
        if response.status_code == 200:
            json_text: dict = response.json()
        else:
            raise WikidataError(f"Got {response.status_code} from Wikidata for {url}")
        if required_property in json_text["claims"]:
            for key in json_text["claims"][required_property]:
                required_value_status = (
                    RequiredValueStatus.PRESENT
                    if key["mainsnak"]["datavalue"]["value"]["id"] == required_value
                    else RequiredValueStatus.INCORRECT
                )
        else:
            required_value_status = RequiredValueStatus.MISSING
        return required_value_status

    def _process_qualifiers_in_shape_claim(self):
        self.__find_allowed_qualifiers__()
        if len(self.allowed_qualifiers) > 0:
            self.conditions.missing_qualifiers.extend(self.allowed_qualifiers)

    def process_allowed(self):
        """This should be rewritten and clarified

        Dennis does not like that the different variables are mixed
        because it makes it harder to understand
        """
        if self.conditions.required_value_status == RequiredValueStatus.PRESENT:
            # FIXME why is the allowed status dependent on the qualifiers?
            self.conditions.property_status = (
                PropertyStatus.CORRECT
                if self.conditions.missing_qualifiers == ""
                else self.conditions.missing_qualifiers
            )
        if self.conditions.required_value_status == RequiredValueStatus.INCORRECT:
            # Check if extra is allowed in the shape and permit it in that case
            if self.conditions.extra == Extra.EXTRA:
                self.conditions.property_status = PropertyStatus.ALLOWED
            else:
                if self.conditions.missing_qualifiers == "":
                    self.conditions.property_status = PropertyStatus.ALLOWED
                else:
                    # Why this? What does it do?
                    self.conditions.property_status = self.conditions.missing_qualifiers
        if (
            self.conditions.property_status == PropertyStatus.INCORRECT
            and self.conditions.extra == Extra.EXTRA
        ):
            self.conditions.property_status = PropertyStatus.ALLOWED
        if self.conditions.required_value_status == RequiredValueStatus.MISSING:
            # FIXME What does this do?
            self.conditions.property_status = self.conditions.required_value_status

    def __find_allowed_qualifiers__(self):
        for qualifier in self.shape_claim["qualifiers"]:
            if (
                "qualifiers" in self.statement
                and qualifier not in self.statement["qualifiers"]
            ):
                self.allowed_qualifiers.append(qualifier)
