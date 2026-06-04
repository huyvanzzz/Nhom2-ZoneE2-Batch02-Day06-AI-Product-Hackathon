from typing import Literal

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    title: str
    url: str
    summary: str = ""


class AssistRequest(BaseModel):
    query: str


class AssistResponse(BaseModel):
    status: Literal["ok", "needs_input", "error"]
    answer: str | None = None
    sources: list[SourceRef] = Field(default_factory=list)
    follow_up_question: str | None = None
