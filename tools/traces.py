from typing import Dict, List


def get_trace(service: str) -> Dict:
    """
    Mock distributed trace retrieval tool.

    Later this will integrate with:
    - OpenTelemetry
    - Datadog APM
    - Jaeger
    - Zipkin
    """

    return {
        "service": service,
        "trace_id": "trace-12345",
        "spans": [
            {
                "span": "request_received",
                "duration_ms": 12
            },
            {
                "span": "auth_service",
                "duration_ms": 45
            },
            {
                "span": "checkout_service",
                "duration_ms": 110
            },
            {
                "span": "db_query_slow",
                "duration_ms": 620
            },
            {
                "span": "response_delayed",
                "duration_ms": 80
            }
        ]
    }