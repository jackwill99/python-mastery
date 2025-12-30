from __future__ import annotations

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Senior Pro-Tip: Similar to OpenTelemetry SDK in Node/Java/Dart; set a global tracer provider once, then instrument FastAPI to emit spans to Jaeger/Honeycomb.


def configure_tracing(service_name: str = "payment-api") -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(provider)


app = FastAPI(title="Traced API", version="1.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> FastAPI:
    configure_tracing()
    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
    return app


if __name__ == "__main__":
    import uvicorn

    create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

