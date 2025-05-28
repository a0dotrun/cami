from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatEntry(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class Claim(BaseModel):
    purpose: str
    amount: float
    status: str = Field(default="pending")


class ClaimHistory(BaseModel):
    claims: list[Claim] = []


class LongRunningTask(BaseModel):
    id: str
    args: dict[str, Any] | None = Field(
        default=None,
    )
    name: str | None = Field(
        default=None,
    )


class LongRunningTasks(BaseModel):
    entries: list[LongRunningTask] = []
