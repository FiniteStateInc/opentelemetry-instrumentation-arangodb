from setuptools import setup, find_packages

setup(
    name="opentelemetry-instrumentation-arangodb",
    version="0.1.0",
    description="OpenTelemetry instrumentation for python-arango",
    author="Wyatt Walter",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-instrumentation",
        "python-arango"
    ],
    extras_require={
        "instruments": []
    },
    entry_points={
        "opentelemetry_instrumentor": [
            "arangodb = opentelemetry_instrumentation_arangodb.arangodb_instrumentor:ArangoDBInstrumentor"
        ]
    },
)
