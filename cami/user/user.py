import datetime
from typing import Optional # Still good practice to use for clarity, though `| None` works too

from pydantic import BaseModel


class User(BaseModel):
    id: str
    first_name: str
    last_name: str | None = None  # Optional, defaults to None
    phone_number: Optional[str] = None  # Optional, defaults to None
    email: str | None = None  # Optional, defaults to None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def to_dict(self):
        return self.model_dump()
