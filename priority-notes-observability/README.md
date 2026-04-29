# Priority Notes Observability

Отдельный платформенный каталог для лабораторной работы №7.

Здесь находится стек наблюдаемости:

- Prometheus
- Grafana
- Grafana Tempo
- Kubernetes ServiceMonitor

Кода приложения и PostgreSQL здесь нет.

## Локальный запуск только стека

Этот вариант удобен, если API уже запущен на хосте на порту `8080`.

```bash
docker compose up -d
```

Порты:

- Prometheus: `http://localhost:19090`
- Grafana: `http://localhost:13001`
- Tempo: `http://localhost:13200`
- OTLP HTTP: `http://localhost:14318`

Grafana:

```text
login: admin
password: admin
```

Для приложения на хосте:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:14318
OTEL_SERVICE_NAME=priority-notes-api
```

Prometheus скрейпит:

```text
host.docker.internal:8080/metrics
```

## Kubernetes

Сначала установить kube-prometheus-stack через Helm:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace observability --create-namespace
```

Затем применить Tempo и ServiceMonitor:

```bash
kubectl apply -f k8s/
```

В приложении должен быть endpoint:

```text
/metrics
```

И переменные:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo.observability.svc.cluster.local:4318
OTEL_SERVICE_NAME=priority-notes-api
```
