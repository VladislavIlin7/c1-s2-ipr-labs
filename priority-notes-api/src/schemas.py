from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class NoteCategory(StrEnum):
    urgent_important = "urgent_important"
    not_urgent_important = "not_urgent_important"
    urgent_not_important = "urgent_not_important"
    not_urgent_not_important = "not_urgent_not_important"


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=5000)
    is_important: bool
    is_urgent: bool


class Note(BaseModel):
    id: str
    title: str
    content: str
    is_important: bool
    is_urgent: bool
    category: NoteCategory
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Stats(BaseModel):
    created_count: int
    existing_count: int
    categories: dict[NoteCategory, int]


class ErrorResponse(BaseModel):
    detail: str

