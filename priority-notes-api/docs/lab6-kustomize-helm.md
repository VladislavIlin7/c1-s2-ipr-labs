# Лабораторная работа №6: Kustomize и Helm

## Цель

Разделить приложение и инфраструктуру, описать приложение через Kustomize и Helm, а PostgreSQL вынести в отдельный инфраструктурный каталог.

## Разделение каталогов

Инфраструктура:

```text
../priority-notes-infra/
```

Там находится только PostgreSQL:

- StatefulSet
- Headless Service
- ConfigMap
- Secret
- PVC через `volumeClaimTemplates`
- Kustomize base + overlays
- Helm chart + values

Приложение:

```text
priority-notes-api/k8s/
```

Там находится только `Priority Notes API`:

- Deployment
- Service
- ConfigMap
- Secret с `DATABASE_URL`
- HPA
- Ingress для prod overlay
- Kustomize base + overlays
- Helm chart + values

В приложении нет манифестов PostgreSQL. API подключается к базе по контракту из инфраструктурного README.

## Почему PostgreSQL в инфраструктуре

PostgreSQL является stateful-компонентом. У него другой жизненный цикл, другие требования к бэкапам, секретам и данным.

Для PostgreSQL используется `StatefulSet`, потому что он дает:

- стабильное имя Pod: `postgres-0`
- стабильное DNS-имя через Headless Service
- постоянное хранилище через PVC

Headless Service:

```text
postgres
```

DNS dev:

```text
postgres-0.postgres.priority-notes-dev.svc.cluster.local
```

DNS prod:

```text
postgres-0.postgres.priority-notes-infra-prod.svc.cluster.local
```

## Часть A. Инфраструктура

Проверка StorageClass:

```bash
kubectl get storageclass
```

### Инфраструктура через Kustomize

Dev:

```bash
cd ../priority-notes-infra
kubectl apply -k k8s/kustomization/overlays/dev
```

Prod:

```bash
cd ../priority-notes-infra
kubectl apply -k k8s/kustomization/overlays/prod
```

Проверка:

```bash
kubectl get pods,pvc -n priority-notes-dev -l app=postgres
kubectl logs statefulset/postgres -n priority-notes-dev
```

### Инфраструктура через Helm

Dev:

```bash
cd ../priority-notes-infra
helm upgrade --install priority-notes-db ./k8s/helm/postgres-infra \
  --namespace priority-notes-dev --create-namespace \
  -f ./k8s/helm/postgres-infra/values-dev.yaml
```

Prod:

```bash
cd ../priority-notes-infra
helm upgrade --install priority-notes-db ./k8s/helm/postgres-infra \
  --namespace priority-notes-infra-prod --create-namespace \
  -f ./k8s/helm/postgres-infra/values-prod.yaml
```

## Часть B. Приложение через Kustomize

Структура:

```text
k8s/kustomization/
├── base/
└── overlays/
    ├── dev/
    └── prod/
```

Base содержит общие манифесты приложения:

- Deployment
- Service
- ConfigMap

Overlays добавляют:

- namespace
- Secret с `DATABASE_URL`
- HPA
- prod Ingress
- patches для реплик, ресурсов и Service

Dev:

```bash
kubectl kustomize k8s/kustomization/overlays/dev
kubectl apply -k k8s/kustomization/overlays/dev
```

Prod:

```bash
kubectl kustomize k8s/kustomization/overlays/prod
kubectl apply -k k8s/kustomization/overlays/prod
```

Dev использует базу в том же namespace:

```text
postgresql://notes_user:notes_password@postgres-0.postgres.priority-notes-dev.svc.cluster.local:5432/priority_notes
```

Prod показывает меж-namespace контракт:

```text
postgresql://notes_user:CHANGE_ME@postgres-0.postgres.priority-notes-infra-prod.svc.cluster.local:5432/priority_notes
```

## Часть C. Приложение через Helm

Структура:

```text
k8s/helm/priority-notes-app/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
```

Проверка шаблонов:

```bash
helm template priority-notes-app ./k8s/helm/priority-notes-app \
  --namespace priority-notes-dev \
  -f ./k8s/helm/priority-notes-app/values-dev.yaml
```

Установка dev:

```bash
helm upgrade --install priority-notes-app ./k8s/helm/priority-notes-app \
  --namespace priority-notes-dev --create-namespace \
  -f ./k8s/helm/priority-notes-app/values-dev.yaml
```

Установка prod:

```bash
helm upgrade --install priority-notes-app ./k8s/helm/priority-notes-app \
  --namespace priority-notes-prod --create-namespace \
  -f ./k8s/helm/priority-notes-app/values-prod.yaml
```

Откат:

```bash
helm rollback priority-notes-app 1 -n priority-notes-dev
```

Удаление:

```bash
helm uninstall priority-notes-app -n priority-notes-dev
```

## Проверка приложения

Для dev Service используется NodePort `30080`.

```bash
curl http://localhost:30080/health
curl http://localhost:30080/notes
```

Swagger UI:

```text
http://localhost:30080/docs
```

Создание заметки:

```bash
curl -X POST http://localhost:30080/notes \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Lab 6\",\"description\":\"Kustomize and Helm\",\"important\":true,\"urgent\":false}"
```

## Kustomize vs Helm

| Критерий | Kustomize | Helm |
| --- | --- | --- |
| Подход | Патчи и overlays поверх YAML | Шаблоны Go + values |
| Удобно для | GitOps и нескольких окружений | Пакетирования приложения и параметризации |
| Сильная сторона | Нет отдельного языка шаблонов | Релизы, rollback, values-файлы |
| Минус | Сложную логику описывать неудобно | Нужно следить за шаблонами и values |

В лабораторной используются оба подхода на одном приложении.
