from pydantic import BaseModel


class MembershipResponse(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
