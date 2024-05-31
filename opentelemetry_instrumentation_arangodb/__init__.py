import logging
import functools
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import StatusCode
from arango.aql import AQL

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ArangoDBInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider", trace.get_tracer_provider())
        self._tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)

        if hasattr(AQL, "execute"):
            logger.debug("Instrumenting AQL.execute")
            self._original_method = getattr(AQL, "execute")
            setattr(AQL, "execute", self._get_instrumented_execute())

    def _uninstrument(self, **kwargs):
        if hasattr(AQL, "execute"):
            logger.debug("Uninstrumenting AQL.execute")
            unwrap(AQL, "execute")

    def _get_instrumented_execute(self):
        tracer = self._tracer

        @functools.wraps(self._original_method)
        def instrumented_execute(*args, **kwargs):
            query = args[1] if len(args) > 1 else kwargs.get('query', 'Unknown query')
            dbname = args[0].db_name if len(args) > 0 else kwargs.get('db_name', 'Unknown db')
            with tracer.start_as_current_span("ArangoDB Execute", kind=SpanKind.CLIENT) as span:
                span.set_attribute("db.name", dbname)
                span.set_attribute("db.query", query)
                if kwargs.get('bind_vars'):
                    span.set_attribute("db.bind_vars", str(kwargs.get('bind_vars')))
                try:
                    result = self._original_method(*args, **kwargs)
                    span.set_status(StatusCode.OK)
                except Exception as e:
                    span.set_status(StatusCode.ERROR, str(e))
                    raise e

                try:
                    span.set_attribute("db.cached", result.cached())
                    if result.count() is not None:
                        span.set_attribute("db.count", result.count())
                    if result.statistics() is not None:
                        for key, value in result.statistics().items():
                            span.set_attribute("db." + key, value)
                    if result.warnings():
                        span.set_attribute("db.warnings", str(result.warnings()))
                except Exception as e:
                    logger.debug("Error setting trace attributes: %s", e)
                return result

        return instrumented_execute

arangodb_instrumentor = ArangoDBInstrumentor()
