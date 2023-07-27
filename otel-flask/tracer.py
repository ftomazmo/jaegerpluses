from __future__ import annotations

import json
import logging
import os
from functools import wraps

from flask import request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GrpcOTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HttpOTLPSpanExporter
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.wsgi import collect_request_attributes
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind, get_tracer_provider, set_tracer_provider

OTLP_COLLECTOR_ADDRESS = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", False)
OTLP_ENABLED = os.environ.get("OTLP_ENABLED", False) == "YES"
OTEL_SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "unknown-service")
OTEL_ENDPOINT_REQUEST_ATTRIBUTE_ENABLED = (
    os.environ.get("OTEL_ENDPOINT_REQUEST_ATTRIBUTE_ENABLED", False) == "YES"
)
OTEL_EXPORTER_OTLP_ENDPOINT_GRPC = (
    os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT_GRPC", False) == "YES"
)

def initialize_tracer(app):
    if not OTLP_ENABLED:
        return

    logging.info(
        "🔭 OpenTelemetry connecting to %s on %s",
        OTLP_COLLECTOR_ADDRESS,
        os.environ.get("NAMESPACE"),
    )
    set_tracer_provider(
        TracerProvider(resource=Resource(attributes={SERVICE_NAME: OTEL_SERVICE_NAME}))
    )
    tracer = get_tracer_provider().get_tracer(__name__)
    if OTEL_EXPORTER_OTLP_ENDPOINT_GRPC:
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(GrpcOTLPSpanExporter(endpoint=OTLP_COLLECTOR_ADDRESS, insecure=True))
        )
    else:
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(HttpOTLPSpanExporter(endpoint=OTLP_COLLECTOR_ADDRESS))
        )

    def span(name):
        return tracer.start_as_current_span(
            name,
            context=extract(request.headers),
            kind=SpanKind.SERVER,
            attributes=collect_request_attributes(request.environ),
        )

    def decorate_with_trace(traced):
        @wraps(traced)
        def in_span(*args, **kws):
            with span(traced.__name__):
                if OTEL_ENDPOINT_REQUEST_ATTRIBUTE_ENABLED and request.is_json:
                    trace.get_current_span().set_attribute(
                        "request_body", json.dumps(request.get_json())
                    )
                return traced(*args, **kws)

        return in_span

    with app.app_context() as context:
        view_handlers = [
            (view, decorate_with_trace(handler))
            for view, handler in context.app.view_functions.items()
        ]
        for view, handler in view_handlers:
            context.app.view_functions[view] = handler

    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    FlaskInstrumentor().instrument_app(app)
