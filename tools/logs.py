from typing import List


def get_logs(service: str) -> List[str]:
    """
    Mock log provider (MVP).

    Simulates structured application logs from:
    - Datadog Logs
    - ELK stack
    - CloudWatch
    """

    return [
        f"[{service}] ERROR: DB query latency spike detected",
        f"[{service}] WARN: increased response time on /checkout endpoint",
        f"[{service}] INFO: retry succeeded after timeout",
        f"[{service}] ERROR: connection pool nearing limit",
        f"[{service}] INFO: request completed with elevated latency"
    ]