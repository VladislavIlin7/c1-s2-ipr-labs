# Лабораторная работа №5: Основы Kubernetes

## Цель

Развернуть приложение `Priority Notes API` в Kubernetes с помощью YAML-манифестов, проверить работу Deployment, Service, Namespace, ConfigMap, Secret, PersistentVolumeClaim, Ingress и HPA.

## Что разворачивается

Приложение:

- FastAPI REST API
- SQLite для хранения заметок
- Docker-образ `priority-notes-api:1.0`
- HTTP-порт контейнера `8000`

SQLite хранится в файле `/data/notes.db`. Этот путь передается через переменную окружения `NOTES_DB_PATH`, а каталог `/data` подключается через PersistentVolumeClaim.

## Структура Kubernetes-манифестов

```text
k8s-manifests/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── persistent-volume-claim.yaml
├── deployment.yaml
├── service.yaml
├── ingress.yaml
└── hpa.yaml
```

## Подготовка Docker Desktop Kubernetes

Проверить, что Kubernetes включен:

```bash
kubectl cluster-info
kubectl get nodes
kubectl config current-context
```

Для Docker Desktop ожидаемый контекст:

```bash
docker-desktop
```

Если выбран другой контекст:

```bash
kubectl config use-context docker-desktop
```

## Сборка Docker-образа

Из каталога `priority-notes-api`:

```bash
docker build -t priority-notes-api:1.0 .
```

Проверка:

```bash
docker images | findstr priority-notes-api
```

В Docker Desktop Kubernetes локальный образ доступен кластеру, поэтому для локальной лабораторной публикация в registry не обязательна.

## Применение манифестов

```bash
kubectl apply -f k8s-manifests/
```

Или по шагам:

```bash
kubectl apply -f k8s-manifests/namespace.yaml
kubectl apply -f k8s-manifests/configmap.yaml
kubectl apply -f k8s-manifests/secret.yaml
kubectl apply -f k8s-manifests/persistent-volume-claim.yaml
kubectl apply -f k8s-manifests/deployment.yaml
kubectl apply -f k8s-manifests/service.yaml
kubectl apply -f k8s-manifests/ingress.yaml
kubectl apply -f k8s-manifests/hpa.yaml
```

## Проверка развертывания

```bash
kubectl get namespace lab5
kubectl get deployments -n lab5
kubectl get pods -n lab5
kubectl get services -n lab5
kubectl get pvc -n lab5
kubectl get hpa -n lab5
```

Подробная информация:

```bash
kubectl describe deployment priority-notes-deployment -n lab5
kubectl describe service priority-notes-service -n lab5
kubectl describe pvc priority-notes-sqlite-pvc -n lab5
```

Логи:

```bash
kubectl logs deployment/priority-notes-deployment -n lab5
```

## Доступ к приложению

Service имеет тип `NodePort` и порт `30080`.

Открыть:

```text
http://localhost:30080
http://localhost:30080/docs
```

Проверка через командную строку:

```bash
curl http://localhost:30080/health
curl http://localhost:30080/notes
```

Создание заметки:

```bash
curl -X POST http://localhost:30080/notes \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Kubernetes lab\",\"description\":\"Deploy Priority Notes API\",\"important\":true,\"urgent\":true}"
```

Альтернативный доступ через port-forward:

```bash
kubectl port-forward service/priority-notes-service 8080:80 -n lab5
```

После этого API доступен по адресу:

```text
http://localhost:8080/docs
```

## ConfigMap и Secret

ConfigMap `priority-notes-config` хранит обычную конфигурацию:

- `APP_ENV`
- `LOG_LEVEL`
- `NOTES_DB_PATH`

Secret `priority-notes-secret` хранит условный секрет:

- `APP_SECRET_KEY`

В Deployment они подключены через `envFrom`.

## SQLite и PersistentVolumeClaim

Так как приложение использует SQLite, в Kubernetes добавлен PVC:

```text
priority-notes-sqlite-pvc
```

Он монтируется в Pod по пути:

```text
/data
```

Файл базы:

```text
/data/notes.db
```

Для SQLite в учебном варианте задана `replicas: 1`. Масштабирование API с общей SQLite-базой не является хорошей production-практикой. Для нескольких реплик лучше использовать отдельную СУБД, например PostgreSQL.

## Ingress

Манифест `ingress.yaml` описывает доступ через host:

```text
priority-notes.local
```

Для работы нужен Ingress Controller, например Nginx Ingress Controller. Также нужно добавить запись в hosts:

```text
127.0.0.1 priority-notes.local
```

После настройки:

```text
http://priority-notes.local/docs
```

## Horizontal Pod Autoscaler

Манифест `hpa.yaml` задает автоматическое масштабирование:

- минимум `1` Pod
- максимум `3` Pod
- целевая загрузка CPU `60%`

Проверка:

```bash
kubectl get hpa -n lab5
```

Для полноценной работы HPA в локальном кластере должен быть установлен metrics-server.

## Масштабирование вручную

```bash
kubectl scale deployment priority-notes-deployment --replicas=2 -n lab5
kubectl get pods -n lab5
```

Для текущей SQLite-версии после демонстрации лучше вернуть одну реплику:

```bash
kubectl scale deployment priority-notes-deployment --replicas=1 -n lab5
```

## Обновление приложения

Собрать новую версию:

```bash
docker build -t priority-notes-api:2.0 .
```

Обновить Deployment:

```bash
kubectl set image deployment/priority-notes-deployment priority-notes-api=priority-notes-api:2.0 -n lab5
kubectl rollout status deployment/priority-notes-deployment -n lab5
kubectl rollout history deployment/priority-notes-deployment -n lab5
```

Откат:

```bash
kubectl rollout undo deployment/priority-notes-deployment -n lab5
```

## Удаление ресурсов

Удалить все ресурсы лабораторной:

```bash
kubectl delete namespace lab5
```

Или удалить только созданные манифесты:

```bash
kubectl delete -f k8s-manifests/
```
