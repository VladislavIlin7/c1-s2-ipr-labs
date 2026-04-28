# API Documentation

Base URL: `http://localhost:8000`

Данные API сохраняются в SQLite-файл `notes.db`.

## Note structure

```json
{
  "id": 1,
  "title": "Сделать лабораторную",
  "description": "Настроить CI/CD",
  "important": true,
  "urgent": true,
  "quadrant": "do_now"
}
```

## Quadrants

| important | urgent | quadrant |
| --- | --- | --- |
| true | true | do_now |
| true | false | schedule |
| false | true | delegate |
| false | false | delete |

## Health

```http
GET /health
```

Response:

```json
{"status": "ok"}
```

## Create note

```http
POST /notes
Content-Type: application/json
```

Body:

```json
{
  "title": "Study CI/CD",
  "description": "Prepare pipeline",
  "important": true,
  "urgent": true
}
```

Response:

```json
{
  "id": 1,
  "title": "Study CI/CD",
  "description": "Prepare pipeline",
  "important": true,
  "urgent": true,
  "quadrant": "do_now"
}
```

## List notes

```http
GET /notes
```

## Get note by ID

```http
GET /notes/{note_id}
```

## Delete note

```http
DELETE /notes/{note_id}
```
