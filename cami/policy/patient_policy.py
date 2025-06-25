import datetime

from pydantic import BaseModel, Field


class PatientPolicy(BaseModel):
    patient_id: str = Field(..., title="Patient ID")
    policy_id: str = Field(..., title="Policy ID purchased by the patient")
    date_of_purchase: datetime.datetime = Field(..., title="Purchase date of the policy")
    valid_till: datetime.datetime = Field(..., title="Date till the policy is valid")
    sum_insured: int = Field(..., title="Patient sum insured")

    def to_dict(self) -> dict:
        return self.model_dump()
