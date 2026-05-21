from typing import List


def get_logs(service: str) -> List[str]:
    """
    Mock log retrieval tool.

    Later this will integrate with:
    - Datadog Logs
    - ELK Stack
    - CloudWatch
    - Grafana Loki
    """

    return [
        f"[{service}] ERROR: DB query latency spike detected",
        f"[{service}] WARN: increased response time on /checkout",
        f"[{service}] INFO: retry attempt succeeded after timeout"
    ]