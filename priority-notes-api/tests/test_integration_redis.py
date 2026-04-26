import pytest

from src.schemas import NoteCategory, NoteCreate
from src.services.notes_service import NotesService


@pytest.mark.asyncio
async def test_redis_integration_persists_note_with_category_index_and_ttl(real_redis_client):
    service = NotesService(real_redis_client)

    note = await service.create_note(
        NoteCreate(title="Production issue", content="Fix incident", is_important=True, is_urgent=True)
    )

    stored_note = await service.get_note(note.id)
    category_notes = await service.list_notes_by_category(NoteCategory.urgent_important)
    ttl = await real_redis_client.ttl(f"note:{note.id}")

    assert stored_note.id == note.id
    assert [stored.id for stored in category_notes] == [note.id]
    assert ttl > 0

