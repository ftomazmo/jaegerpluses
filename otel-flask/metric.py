import os

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

OTLP_ENABLED = os.environ.get("OTLP_ENABLED", False) == "YES"
OTLP_COLLECTOR_ADDRESS = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", False)
OTEL_SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "unknown-service")
OTEL_EXPORTER_OTLP_ENDPOINT_GRPC = (
    os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT_GRPC", False) == "YES"
)

def initialize_metric():
    if not OTLP_ENABLED or not OTEL_EXPORTER_OTLP_ENDPOINT_GRPC:
        return

    # Service name is required for most backends
    resource = Resource(attributes={
        SERVICE_NAME: OTEL_SERVICE_NAME
    })

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTLP_COLLECTOR_ADDRESS)
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)