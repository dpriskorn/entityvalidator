# from pydantic import BaseModel, Field
#
#
# class ValidateRequest(BaseModel):
#     eid: str = Field(..., description="EntitySchema ID, ex. E100")
#     entity_ids: list[str] = Field(
#         ..., max_length=100, description="Lista med max 100 entity IDs (t.ex. Q42)"
#     )
#     lang: str = Field("en", description="Språkkod, default = en")
