# Priority Notes Infrastructure

Отдельный инфраструктурный каталог для лабораторной работы №6.

Здесь находится только PostgreSQL: StatefulSet, Headless Service, Secret, ConfigMap и PVC через `volumeClaimTemplates`. Манифестов приложения в этом каталоге нет.

## Контракт для приложения

Приложение подключается к PostgreSQL через переменную окружения `DATABASE_URL`.

Dev namespace:

```text
postgresql://notes_user:notes_password@postgres-0.postgres.priority-notes-dev.svc.cluster.local:5432/priority_notes
```

Prod namespace:

```text
postgresql://notes_user:CHANGE_ME@postgres-0.postgres.priority-notes-infra-prod.svc.cluster.local:5432/priority_notes
```

Параметры:

- host: `postgres-0.postgres.<namespace>.svc.cluster.local`
- port: `5432`
- database: `priority_notes`
- user: `notes_user`
- password: из Secret инфраструктуры

## Проверка StorageClass

```bash
kubectl get storageclass
```

## Установка через Kustomize

Dev:

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

Prod:

```bash
kubectl apply -k k8s/kustomization/overlays/prod
```

Проверка:

```bash
kubectl get pods,pvc -n priority-notes-dev -l app=postgres
kubectl logs statefulset/postgres -n priority-notes-dev
```

## Установка через Helm

Dev:

```bash
helm upgrade --install priority-notes-db ./k8s/helm/postgres-infra \
  --namespace priority-notes-dev --create-namespace \
  -f ./k8s/helm/postgres-infra/values-dev.yaml
```

Prod:

```bash
helm upgrade --install priority-notes-db ./k8s/helm/postgres-infra \
  --namespace priority-notes-infra-prod --create-namespace \
  -f ./k8s/helm/postgres-infra/values-prod.yaml
```

Удаление:

```bash
helm uninstall priority-notes-db -n priority-notes-dev
```
