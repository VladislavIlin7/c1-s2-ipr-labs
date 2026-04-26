import pytest


@pytest.mark.asyncio
async def test_health(api_client):
    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_get_list_and_delete_note(api_client):
    create_response = await api_client.post(
        "/notes",
        json={
            "title": "Prepare demo",
            "content": "Show Priority Notes API",
            "is_important": True,
            "is_urgent": False,
        },
    )

    assert create_response.status_code == 201
    note = create_response.json()
    assert note["category"] == "not_urgent_important"

    get_response = await api_client.get(f"/notes/{note['id']}")
    list_response = await api_client.get("/notes")
    category_response = await api_client.get("/notes/category/not_urgent_important")
    stats_response = await api_client.get("/stats")
    delete_response = await api_client.delete(f"/notes/{note['id']}")
    missing_response = await api_client.get(f"/notes/{note['id']}")

    assert get_response.status_code == 200
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert category_response.status_code == 200
    assert len(category_response.json()) == 1
    assert stats_response.json()["created_count"] == 1
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_create_note_validation_error(api_client):
    response = await api_client.post(
        "/notes",
        json={"title": "", "content": "", "is_important": True, "is_urgent": True},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_category_returns_validation_error(api_client):
    response = await api_client.get("/notes/category/unknown")

    assert response.status_code == 422

