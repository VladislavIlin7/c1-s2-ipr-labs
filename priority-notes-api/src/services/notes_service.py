import json
import logging
from datetime import UTC, datetime
from uuid import uuid4

from src.config import get_settings
from src.schemas import Note, NoteCategory, NoteCreate, Stats

logger = logging.getLogger(__name__)

NOTE_KEY_PREFIX = "note:"
CATEGORY_KEY_PREFIX = "category:"
CREATED_COUNT_KEY = "stats:created_count"


class NoteNotFoundError(Exception):
    pass


def determine_category(is_important: bool, is_urgent: bool) -> NoteCategory:
    if is_important and is_urgent:
        return NoteCategory.urgent_important
    if is_important and not is_urgent:
        return NoteCategory.not_urgent_important
    if not is_important and is_urgent:
        return NoteCategory.urgent_not_important
    return NoteCategory.not_urgent_not_important


class NotesService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.settings = get_settings()

    async def create_note(self, payload: NoteCreate) -> Note:
        note = Note(
            id=str(uuid4()),
            title=payload.title,
            content=payload.content,
            is_important=payload.is_important,
            is_urgent=payload.is_urgent,
            category=determine_category(payload.is_important, payload.is_urgent),
            created_at=datetime.now(UTC),
        )

        note_key = self._note_key(note.id)
        category_key = self._category_key(note.category)
        note_json = note.model_dump_json()

        if note.is_urgent:
            await self.redis.set(note_key, note_json, ex=self.settings.urgent_note_ttl_seconds)
        else:
            await self.redis.set(note_key, note_json)

        await self.redis.sadd(category_key, note.id)
        await self.redis.incr(CREATED_COUNT_KEY)
        logger.info("Created note %s in category %s", note.id, note.category)
        return note

    async def get_note(self, note_id: str) -> Note:
        raw_note = await self.redis.get(self._note_key(note_id))
        if raw_note is None:
            logger.warning("Note %s was not found", note_id)
            raise NoteNotFoundError(f"Note {note_id} was not found")
        return self._load_note(raw_note)

    async def list_notes(self) -> list[Note]:
        notes: list[Note] = []
        async for key in self.redis.scan_iter(match=f"{NOTE_KEY_PREFIX}*"):
            raw_note = await self.redis.get(key)
            if raw_note is not None:
                notes.append(self._load_note(raw_note))
        return sorted(notes, key=lambda note: note.created_at, reverse=True)

    async def list_notes_by_category(self, category: NoteCategory) -> list[Note]:
        note_ids = await self.redis.smembers(self._category_key(category))
        notes: list[Note] = []

        for note_id in note_ids:
            raw_note = await self.redis.get(self._note_key(note_id))
            if raw_note is None:
                await self.redis.srem(self._category_key(category), note_id)
                continue
            notes.append(self._load_note(raw_note))

        return sorted(notes, key=lambda note: note.created_at, reverse=True)

    async def delete_note(self, note_id: str) -> None:
        note = await self.get_note(note_id)
        deleted_count = await self.redis.delete(self._note_key(note_id))
        await self.redis.srem(self._category_key(note.category), note_id)

        if deleted_count == 0:
            raise NoteNotFoundError(f"Note {note_id} was not found")
        logger.info("Deleted note %s", note_id)

    async def get_stats(self) -> Stats:
        created_count = int(await self.redis.get(CREATED_COUNT_KEY) or 0)
        categories: dict[NoteCategory, int] = {}

        for category in NoteCategory:
            notes = await self.list_notes_by_category(category)
            categories[category] = len(notes)

        return Stats(
            created_count=created_count,
            existing_count=sum(categories.values()),
            categories=categories,
        )

    @staticmethod
    def _note_key(note_id: str) -> str:
        return f"{NOTE_KEY_PREFIX}{note_id}"

    @staticmethod
    def _category_key(category: NoteCategory) -> str:
        return f"{CATEGORY_KEY_PREFIX}{category.value}"

    @staticmethod
    def _load_note(raw_note: str) -> Note:
        return Note.model_validate(json.loads(raw_note))

