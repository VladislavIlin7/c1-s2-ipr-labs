# Priority Notes API

Учебный REST API для заметок по матрице Эйзенхауэра. Проект показывает, как связать FastAPI, async Redis, Pydantic, pytest, Docker и GitLab CI/CD в небольшой, понятный сервис.

## Стек

- Python 3.11+
- FastAPI
- Redis async client
- Pydantic
- pytest, pytest-asyncio, pytest-cov
- httpx
- Docker, Docker Compose
- GitLab CI/CD

## Структура проекта

```text
priority-notes-api/
├── README.md
├── LICENSE
├── .gitignore
├── .gitlab-ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── src/
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   ├── services/
│   │   └── notes_service.py
│   └── storage/
│       └── redis_client.py
├── tests/
│   ├── conftest.py
│   ├── test_notes_service.py
│   ├── test_api.py
│   └── test_integration_redis.py
└── docs/
    └── api.md
```

## Как это работает

Redis используется для хранения:

- заметок в ключах `note:{id}`;
- индексов категорий в множествах `category:{category}`;
- счетчика созданных заметок `stats:created_count`;
- TTL для срочных заметок.

Категория определяется в функции `determine_category`:

- `urgent_important` - важные и срочные;
- `not_urgent_important` - важные и несрочные;
- `urgent_not_important` - неважные и срочные;
- `not_urgent_not_important` - неважные и несрочные.

## Локальный запуск

Нужен Python 3.11+ и запущенный Redis.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export REDIS_URL=redis://localhost:6379/0
uvicorn src.main:app --reload
```

Для PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:REDIS_URL = "redis://localhost:6379/0"
uvicorn src.main:app --reload
```

API будет доступен на `http://localhost:8000`.

## Запуск через Docker Compose

```bash
docker compose up --build
```

Сервисы:

- `app` - FastAPI приложение на порту `8000`;
- `redis` - Redis на порту `6379`.

Проверка:

```bash
curl http://localhost:8000/health
```

## Тесты и coverage

Unit и API-тесты используют in-memory fake Redis. Интеграционный тест подключается к Redis по `REDIS_URL`; если Redis недоступен локально, он будет пропущен.

```bash
pytest --cov=src --cov-fail-under=70 --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=junit.xml
```

Ожидаемое покрытие проекта: больше 70%.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Проверка приложения и Redis |
| `POST` | `/notes` | Создать заметку |
| `GET` | `/notes` | Получить все заметки |
| `GET` | `/notes/{note_id}` | Получить заметку по ID |
| `DELETE` | `/notes/{note_id}` | Удалить заметку |
| `GET` | `/notes/category/{category}` | Получить заметки по категории |
| `GET` | `/stats` | Получить статистику |

Подробное описание API находится в [docs/api.md](docs/api.md).

## Пример запроса

```bash
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prepare release",
    "content": "Check tests and publish image",
    "is_important": true,
    "is_urgent": true
  }'
```

## Переменные окружения

| Variable | Default | Description |
| --- | --- | --- |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `URGENT_NOTE_TTL_SECONDS` | `86400` | TTL для срочных заметок |
| `LOG_LEVEL` | `INFO` | Уровень логирования |

## GitLab CI/CD

Pipeline описан в `.gitlab-ci.yml` и содержит стадии:

- `test` - поднимает Redis service, ставит зависимости, запускает pytest, генерирует junit и coverage reports;
- `build` - собирает Docker image после успешных тестов и проверяет, что контейнер стартует;
- `publish` - публикует image в GitLab Container Registry.

В pipeline используются:

- `rules` вместо `only/except`;
- переменные окружения GitLab Container Registry;
- pip cache;
- artifacts для `junit.xml` и `coverage.xml`;
- Redis service для интеграционных тестов.

## Разработчик

Учебный проект подготовлен для лабораторной работы и демонстрации production-like структуры небольшого API-сервиса.

## Лицензия

MIT. См. [LICENSE](LICENSE).
