from fastapi import FastAPI, HTTPException

from src import storage
from src.models import Note, NoteCreate

app = FastAPI(title="Priority Notes API")


@app.get("/")
def root():
    return {"message": "Priority Notes API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes")
def get_notes():
    return storage.get_notes()


@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    return storage.create_note(note)


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    note = storage.get_note(note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    deleted = storage.delete_note(note_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"message": "Note deleted"}
