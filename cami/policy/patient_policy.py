import datetime

from pydantic import BaseModel, Field

from .policy import Policy


class PatientPolicy(BaseModel):
    patient_id: str = Field(..., title="Patient ID")
    policy_id: str = Field(..., title="Policy ID purchased by the patient")
    date_of_purchase: datetime.datetime = Field(..., title="Date of purchase")

    def to_dict(self) -> dict:
        return self.model_dump()
