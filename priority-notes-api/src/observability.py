import os
import time
from contextlib import nullcontext

from fastapi import Response

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ModuleNotFoundError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    Counter = None
    Histogram = None
    generate_latest = None

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ModuleNotFoundError:
    trace = None


if Counter and Histogram:
    HTTP_REQUESTS_TOTAL = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "route", "status_code"],
    )
    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "route"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
    )
    NOTES_CREATED_TOTAL = Counter(
        "notes_created_total",
        "Total created notes by Eisenhower quadrant",
        ["quadrant"],
    )
else:
    HTTP_REQUESTS_TOTAL = None
    HTTP_REQUEST_DURATION_SECONDS = None
    NOTES_CREATED_TOTAL = None


def setup_tracing():
    if trace is None:
        return None

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return None

    service_name = os.getenv("OTEL_SERVICE_NAME", "priority-notes-api")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


def get_route_template(request):
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return route.path
    return request.url.path


def record_note_created(quadrant: str):
    if NOTES_CREATED_TOTAL:
        NOTES_CREATED_TOTAL.labels(quadrant=quadrant).inc()


def metrics_response():
    if generate_latest is None:
        return Response("prometheus_client is not installed\n", status_code=503, media_type="text/plain")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def add_observability(app):
    tracer = setup_tracing()

    @app.middleware("http")
    async def observability_middleware(request, call_next):
        start_time = time.perf_counter()
        status_code = 500
        span_context = nullcontext()

        if tracer is not None:
            span_context = tracer.start_as_current_span(f"{request.method} {request.url.path}")

        with span_context as span:
            try:
                response = await call_next(request)
                status_code = response.status_code
                return response
            except Exception as exc:
                if tracer is not None and span is not None:
                    span.record_exception(exc)
                raise
            finally:
                route = get_route_template(request)
                duration = time.perf_counter() - start_time

                if HTTP_REQUESTS_TOTAL and HTTP_REQUEST_DURATION_SECONDS:
                    HTTP_REQUESTS_TOTAL.labels(
                        method=request.method,
                        route=route,
                        status_code=str(status_code),
                    ).inc()
                    HTTP_REQUEST_DURATION_SECONDS.labels(
                        method=request.method,
                        route=route,
                    ).observe(duration)

                if tracer is not None and span is not None:
                    span.set_attribute("http.method", request.method)
                    span.set_attribute("http.route", route)
                    span.set_attribute("http.status_code", status_code)

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return metrics_response()
