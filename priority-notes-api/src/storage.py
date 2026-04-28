import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://notes_user:notes_password@localhost:5432/priority_notes",
)


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    important BOOLEAN NOT NULL,
                    urgent BOOLEAN NOT NULL,
                    quadrant TEXT NOT NULL
                )
                """
            )


def row_to_note(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "important": row["important"],
        "urgent": row["urgent"],
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
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, important, urgent, quadrant
                FROM notes
                ORDER BY id
                """
            )
            rows = cursor.fetchall()
    return [row_to_note(row) for row in rows]


def create_note(note):
    init_db()
    quadrant = get_quadrant(note.important, note.urgent)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notes (title, description, important, urgent, quadrant)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    note.title,
                    note.description,
                    note.important,
                    note.urgent,
                    quadrant,
                ),
            )
            note_id = cursor.fetchone()["id"]

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
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, important, urgent, quadrant
                FROM notes
                WHERE id = %s
                """,
                (note_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return row_to_note(row)


def delete_note(note_id: int) -> bool:
    init_db()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            return cursor.rowcount > 0


def reset_storage():
    init_db()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE notes RESTART IDENTITY")
