import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "notes.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                important INTEGER NOT NULL,
                urgent INTEGER NOT NULL,
                quadrant TEXT NOT NULL
            )
            """
        )


def row_to_note(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "important": bool(row["important"]),
        "urgent": bool(row["urgent"]),
        "quadrant": row["quadrant"],
    }


def get_quadrant(important: bool, urgent: bool) -> str:
    if important and urgent:
        return "do_now"
    if important and not urgent:
        return "schedule"
    if not important and urgent:
        return "delegate"
    return "delete"


def get_notes():
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, description, important, urgent, quadrant FROM notes ORDER BY id"
        ).fetchall()
    return [row_to_note(row) for row in rows]


def create_note(note):
    init_db()
    quadrant = get_quadrant(note.important, note.urgent)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO notes (title, description, important, urgent, quadrant)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                note.title,
                note.description,
                int(note.important),
                int(note.urgent),
                quadrant,
            ),
        )
        note_id = cursor.lastrowid

    return {
        "id": note_id,
        "title": note.title,
        "description": note.description,
        "important": note.important,
        "urgent": note.urgent,
        "quadrant": quadrant,
    }


def get_note(note_id: int):
    init_db()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, description, important, urgent, quadrant
            FROM notes
            WHERE id = ?
            """,
            (note_id,),
        ).fetchone()

    if row is None:
        return None

    return row_to_note(row)


def delete_note(note_id: int) -> bool:
    init_db()
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return cursor.rowcount > 0


def reset_storage():
    init_db()
    with get_connection() as connection:
        connection.execute("DELETE FROM notes")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'notes'")


init_db()
