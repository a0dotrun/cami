import datetime

from pydantic import BaseModel, Field


class UserPolicy(BaseModel):
    user_id: str = Field(..., title="User ID")
    policy_id: str = Field(..., title="Policy ID purchased by the user")
    date_of_purchase: datetime.datetime = Field(..., title="Purchase date of the policy")
    valid_till: datetime.datetime = Field(..., title="Date till the policy is valid")
    sum_insured: int = Field(..., title="User sum insured")

    def __init__(self, **kwargs):
        kwargs["date_of_purchase"] = datetime.datetime.now(datetime.timezone.utc)
        kwargs["valid_till"] = kwargs["date_of_purchase"]
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        return self.model_dump()
