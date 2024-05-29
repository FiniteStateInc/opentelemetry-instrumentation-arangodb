from arango import ArangoClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("example")

client = ArangoClient()
db = client.db("test", username="root", password="password")

# Manually create a root span
with tracer.start_as_current_span("root-span") as root_span:
    ret = db.aql.execute("FOR doc IN test FILTER doc.test == true RETURN doc")
