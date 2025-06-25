import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(..., title="User ID")
    first_name: str = Field(..., title="User First Name")
    last_name: str = Field(..., title="User First Name")
    phone_number: str = Field(..., title="User Phone")
    email: str = Field(..., title="User Email")
    created_at: datetime.datetime = Field(..., title="User Creation Date")
    updated_at: datetime.datetime = Field(..., title="User Update Date")

    def to_dict(self):
        return self.model_dump()
