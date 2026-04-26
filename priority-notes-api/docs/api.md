# Priority Notes API

Base URL for local development: `http://localhost:8000`.

## Categories

| Category | Meaning |
| --- | --- |
| `urgent_important` | Important and urgent |
| `not_urgent_important` | Important and not urgent |
| `urgent_not_important` | Not important and urgent |
| `not_urgent_not_important` | Not important and not urgent |

## Endpoints

### GET /health

Checks API and Redis availability.

Response:

```json
{
  "status": "ok"
}
```

### POST /notes

Creates a note. The category is calculated by the backend from `is_important` and `is_urgent`.
Urgent notes receive Redis TTL, non-urgent notes are stored without TTL.

Request:

```json
{
  "title": "Prepare report",
  "content": "Finish the quarterly report",
  "is_important": true,
  "is_urgent": true
}
```

Response `201 Created`:

```json
{
  "id": "f1c1f64a-7d1f-4c1f-b65f-b9d4a550f27b",
  "title": "Prepare report",
  "content": "Finish the quarterly report",
  "is_important": true,
  "is_urgent": true,
  "category": "urgent_important",
  "created_at": "2026-04-27T00:00:00Z"
}
```

### GET /notes

Returns all existing notes, sorted by creation date descending.

### GET /notes/{note_id}

Returns a note by ID.

Errors:

| Status | Reason |
| --- | --- |
| `404` | Note does not exist or expired |

### DELETE /notes/{note_id}

Deletes a note and removes it from the category index.

Response: `204 No Content`.

### GET /notes/category/{category}

Returns notes from one Eisenhower matrix category.

Example:

```bash
curl http://localhost:8000/notes/category/urgent_important
```

### GET /stats

Returns creation counter and current number of notes per category.

Response:

```json
{
  "created_count": 10,
  "existing_count": 8,
  "categories": {
    "urgent_important": 2,
    "not_urgent_important": 3,
    "urgent_not_important": 1,
    "not_urgent_not_important": 2
  }
}
```

## Redis Keys

| Key | Type | Purpose |
| --- | --- | --- |
| `note:{id}` | String JSON | Note body |
| `category:{category}` | Set | Note IDs by category |
| `stats:created_count` | String integer | Total created notes counter |

