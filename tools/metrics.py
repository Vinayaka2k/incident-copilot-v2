from typing import Dict


def get_metrics(service: str) -> Dict:
    """
    Mock metrics provider (MVP).

    Simulates metrics from:
    - Prometheus
    - Datadog Metrics
    - Grafana
    """

    return {
        "service": service,

        # latency signals
        "latency_p95": 820,
        "latency_avg": 410,

        # error signals
        "error_rate": 0.04,

        # system health
        "cpu_usage": 0.79,
        "memory_usage": 0.68,

        # traffic
        "request_count": 12450,

        # DB-specific signal (important for incidents)
        "db_latency_ms": 320
    }