import pytest

from src.schemas import NoteCategory, NoteCreate
from src.services.notes_service import NoteNotFoundError, NotesService, determine_category


@pytest.mark.parametrize(
    ("is_important", "is_urgent", "expected"),
    [
        (True, True, NoteCategory.urgent_important),
        (True, False, NoteCategory.not_urgent_important),
        (False, True, NoteCategory.urgent_not_important),
        (False, False, NoteCategory.not_urgent_not_important),
    ],
)
def test_determine_category(is_important, is_urgent, expected):
    assert determine_category(is_important, is_urgent) == expected


@pytest.mark.asyncio
async def test_create_urgent_note_sets_ttl(notes_service: NotesService, fake_redis):
    note = await notes_service.create_note(
        NoteCreate(title="Deadline", content="Finish report", is_important=True, is_urgent=True)
    )

    assert note.category == NoteCategory.urgent_important
    assert await fake_redis.ttl(f"note:{note.id}") == 86400
    assert await fake_redis.get("stats:created_count") == "1"


@pytest.mark.asyncio
async def test_create_not_urgent_note_has_no_ttl(notes_service: NotesService, fake_redis):
    note = await notes_service.create_note(
        NoteCreate(title="Plan", content="Think about roadmap", is_important=True, is_urgent=False)
    )

    assert note.category == NoteCategory.not_urgent_important
    assert await fake_redis.ttl(f"note:{note.id}") == -1


@pytest.mark.asyncio
async def test_get_list_and_delete_note(notes_service: NotesService):
    note = await notes_service.create_note(
        NoteCreate(title="Call", content="Call customer", is_important=False, is_urgent=True)
    )

    assert (await notes_service.get_note(note.id)).id == note.id
    assert [stored.id for stored in await notes_service.list_notes()] == [note.id]

    await notes_service.delete_note(note.id)

    with pytest.raises(NoteNotFoundError):
        await notes_service.get_note(note.id)


@pytest.mark.asyncio
async def test_list_notes_by_category_and_stats(notes_service: NotesService):
    urgent_note = await notes_service.create_note(
        NoteCreate(title="Pay", content="Pay invoice", is_important=True, is_urgent=True)
    )
    await notes_service.create_note(
        NoteCreate(title="Read", content="Read article", is_important=False, is_urgent=False)
    )

    urgent_notes = await notes_service.list_notes_by_category(NoteCategory.urgent_important)
    stats = await notes_service.get_stats()

    assert [note.id for note in urgent_notes] == [urgent_note.id]
    assert stats.created_count == 2
    assert stats.existing_count == 2
    assert stats.categories[NoteCategory.urgent_important] == 1

