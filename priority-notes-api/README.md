# Priority Notes API

Учебный REST API для создания заметок по матрице Эйзенхауэра.

Данные сохраняются в PostgreSQL. Приложение подключается к базе через переменную окружения `DATABASE_URL`.

## Возможности

- Создание заметок
- Получение списка заметок
- Получение заметки по ID
- Удаление заметки
- Хранение заметок в PostgreSQL
- Автоматическое определение квадранта:
  - do_now
  - schedule
  - delegate
  - delete

## Запуск PostgreSQL локально

```bash
docker run --name priority-notes-postgres \
  -e POSTGRES_DB=priority_notes \
  -e POSTGRES_USER=notes_user \
  -e POSTGRES_PASSWORD=notes_password \
  -p 5432:5432 \
  -d postgres:16-alpine
```

## Запуск API локально

```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql://notes_user:notes_password@localhost:5432/priority_notes
uvicorn src.main:app --reload
```

Для PowerShell:

```powershell
$env:DATABASE_URL = "postgresql://notes_user:notes_password@localhost:5432/priority_notes"
uvicorn src.main:app --reload
```

## Запуск тестов

Перед тестами должен быть доступен PostgreSQL.

```bash
pytest --cov=src
```

## Docker

```bash
docker build -t priority-notes-api .
docker run -p 8000:8000 ^
  -e DATABASE_URL=postgresql://notes_user:notes_password@host.docker.internal:5432/priority_notes ^
  priority-notes-api
```

Dockerfile использует multi-stage build.

## PostgreSQL

Таблица `notes` создается автоматически со следующими полями:

- `id`
- `title`
- `description`
- `important`
- `urgent`
- `quadrant`

## Kubernetes

Для лабораторной работы №5 добавлены Kubernetes-манифесты в каталоге `k8s-manifests/`.

Основной запуск:

```bash
docker build -t priority-notes-api:1.0 .
kubectl apply -f k8s-manifests/
```

После развертывания API доступен через NodePort:

```text
http://localhost:30080/docs
```

Подробная инструкция находится в [docs/lab5-kubernetes.md](docs/lab5-kubernetes.md).

## GitHub Actions secrets

Для публикации Docker-образа в GitHub надо добавить секреты:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Путь: `Settings -> Secrets and variables -> Actions -> New repository secret`.
