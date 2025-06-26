from pydantic import BaseModel, Field


class MembershipResponse(BaseModel):
    user_id: str = Field(validation_alias="id")
    first_name: str
    last_name: str
