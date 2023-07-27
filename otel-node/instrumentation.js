const { Resource }= require("@opentelemetry/resources");
const { OTLPTraceExporter }= require("@opentelemetry/exporter-trace-otlp-grpc");
const { BatchSpanProcessor }= require("@opentelemetry/sdk-trace-base");
const { NodeTracerProvider }= require("@opentelemetry/sdk-trace-node");
const { registerInstrumentations }= require("@opentelemetry/instrumentation");
const { HttpInstrumentation }= require("@opentelemetry/instrumentation-http");
const { ExpressInstrumentation }= require("@opentelemetry/instrumentation-express");
const { getNodeAutoInstrumentations }= require("@opentelemetry/auto-instrumentations-node");
const { FsInstrumentation } = require("@opentelemetry/instrumentation-fs");
const { LongTaskInstrumentation }= require("@opentelemetry/instrumentation-long-task");

function setupOpenTelemetry() {
  registerInstrumentations({
    instrumentations: [
      new HttpInstrumentation(),
      new ExpressInstrumentation(),
      new getNodeAutoInstrumentations(),
      new FsInstrumentation(),
      new LongTaskInstrumentation(),
    ],
  });

  const provider = new NodeTracerProvider({
    resource: Resource.default().merge(new Resource({
      // Identify this service name in our system
      'service.name': process.env.OTEL_SERVICE_NAME || 'nodejs',
    })),
  });

  const collectorTraceExporter = new OTLPTraceExporter({ url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT });

  provider.addSpanProcessor(
    new BatchSpanProcessor(collectorTraceExporter, {
      maxQueueSize: 1000,
      scheduledDelayMillis: 1000,
    }),
  );

  provider.register();
}

if (process.env.OTLP_ENABLED === 'YES') {
  // eslint-disable-next-line max-len
  console.log(`Setting up OpenTelemetry on NODE_ENV=${process.env.NODE_ENV} OTEL_EXPORTER_OTLP_ENDPOINT=${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}`);
  setupOpenTelemetry();
}
