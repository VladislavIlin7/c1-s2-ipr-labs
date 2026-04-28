# Лабораторная работа №5: Основы Kubernetes

## Цель

Развернуть `Priority Notes API` в Kubernetes с помощью YAML-манифестов и показать работу Namespace, Deployment, Service, ConfigMap, Secret, PersistentVolumeClaim, Ingress и HPA.

## Что разворачивается

- FastAPI REST API
- PostgreSQL для хранения заметок
- Docker-образ API `priority-notes-api:1.0`
- PostgreSQL-образ `postgres:16-alpine`
- HTTP-порт API `8000`
- PostgreSQL-порт `5432`

## Структура манифестов

```text
k8s-manifests/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── persistent-volume-claim.yaml
├── postgres-deployment.yaml
├── postgres-service.yaml
├── deployment.yaml
├── service.yaml
├── ingress.yaml
└── hpa.yaml
```

## Сборка образа API

```bash
docker build -t priority-notes-api:1.0 .
docker images | findstr priority-notes-api
```

В Docker Desktop Kubernetes локальный образ доступен кластеру, поэтому для лабораторной публикация в registry не обязательна.

## Применение манифестов

```bash
kubectl config use-context docker-desktop
kubectl apply -f k8s-manifests/
```

## Проверка

```bash
kubectl get namespace lab5
kubectl get deployments -n lab5
kubectl get pods -n lab5
kubectl get services -n lab5
kubectl get pvc -n lab5
kubectl get hpa -n lab5
```

Логи API:

```bash
kubectl logs deployment/priority-notes-deployment -n lab5
```

Логи PostgreSQL:

```bash
kubectl logs deployment/postgres-deployment -n lab5
```

## Доступ к приложению

Service API имеет тип `NodePort` и порт `30080`.

```text
http://localhost:30080/docs
```

Проверка:

```bash
curl http://localhost:30080/health
curl http://localhost:30080/notes
```

Создание заметки:

```bash
curl -X POST http://localhost:30080/notes \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Kubernetes lab\",\"description\":\"Deploy Priority Notes API with PostgreSQL\",\"important\":true,\"urgent\":true}"
```

## ConfigMap и Secret

ConfigMap `priority-notes-config` хранит обычные настройки:

- `APP_ENV`
- `LOG_LEVEL`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Secret `priority-notes-secret` хранит чувствительные данные:

- `APP_SECRET_KEY`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`

API получает `DATABASE_URL` через `envFrom` и подключается к PostgreSQL через Kubernetes Service `postgres-service`.

## PostgreSQL и PersistentVolumeClaim

PostgreSQL хранит данные в PVC:

```text
postgres-pvc
```

PVC монтируется в PostgreSQL Pod по пути:

```text
/var/lib/postgresql/data
```

API больше не хранит файл базы внутри своего Pod, поэтому его можно масштабировать независимо от базы данных.

## Deployment API

API запускается через `priority-notes-deployment`.

Важные параметры:

- `replicas: 2`
- `image: priority-notes-api:1.0`
- `imagePullPolicy: IfNotPresent`
- `livenessProbe` и `readinessProbe` ходят на `/health`
- `resources.requests` и `resources.limits` задают CPU и memory

## Service

`priority-notes-service` имеет тип `NodePort`.

- внутренний порт Service: `80`
- порт контейнера API: `8000`
- внешний порт узла: `30080`

`postgres-service` имеет тип `ClusterIP`, поэтому PostgreSQL доступен только внутри кластера.

## Ingress

Ingress описывает доступ через host:

```text
priority-notes.local
```

Для работы нужен Ingress Controller, например Nginx Ingress Controller, и запись в hosts:

```text
127.0.0.1 priority-notes.local
```

## HPA

`priority-notes-hpa` масштабирует API:

- минимум `1` Pod
- максимум `3` Pod
- целевая загрузка CPU `60%`

Для работы HPA нужен metrics-server.

## Ручное масштабирование

```bash
kubectl scale deployment priority-notes-deployment --replicas=3 -n lab5
kubectl get pods -n lab5
```

## Обновление приложения

```bash
docker build -t priority-notes-api:2.0 .
kubectl set image deployment/priority-notes-deployment priority-notes-api=priority-notes-api:2.0 -n lab5
kubectl rollout status deployment/priority-notes-deployment -n lab5
kubectl rollout history deployment/priority-notes-deployment -n lab5
```

Откат:

```bash
kubectl rollout undo deployment/priority-notes-deployment -n lab5
```

## Удаление ресурсов

```bash
kubectl delete namespace lab5
```
