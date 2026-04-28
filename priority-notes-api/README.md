# Priority Notes API

Учебный REST API для создания заметок по матрице Эйзенхауэра.

Данные сохраняются в SQLite-файл `notes.db`, который создается автоматически при запуске приложения.

## Возможности

- Создание заметок
- Получение списка заметок
- Получение заметки по ID
- Удаление заметки
- Хранение заметок в SQLite
- Автоматическое определение квадранта:
  - do_now
  - schedule
  - delegate
  - delete

## Запуск локально

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Запуск тестов

```bash
pytest --cov=src
```

## Docker

```bash
docker build -t priority-notes-api .
docker run -p 8000:8000 priority-notes-api
```

Dockerfile использует multi-stage build.

## SQLite

Приложение использует стандартный модуль Python `sqlite3`, поэтому отдельная зависимость для SQLite не нужна.

Таблица `notes` создается автоматически со следующими полями:

- `id`
- `title`
- `description`
- `important`
- `urgent`
- `quadrant`

## GitHub Actions secrets

Для публикации Docker-образа в GitHub надо добавить секреты:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Путь: `Settings -> Secrets and variables -> Actions -> New repository secret`.
