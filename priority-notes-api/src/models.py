from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    description: str = ""
    important: bool
    urgent: bool


class Note(NoteCreate):
    id: int
    quadrant: str
