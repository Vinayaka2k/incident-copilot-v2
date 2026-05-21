from typing import Dict


def get_trace(service: str) -> Dict:
    """
    Mock distributed trace provider (MVP).

    Simulates OpenTelemetry / Jaeger / Datadog APM style traces.
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
                "span": "db_query",
                "duration_ms": 620
            },
            {
                "span": "response_sent",
                "duration_ms": 80
            }
        ]
    }