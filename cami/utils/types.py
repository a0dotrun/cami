from typing import Literal

from pydantic import BaseModel


class ChatEntry(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
