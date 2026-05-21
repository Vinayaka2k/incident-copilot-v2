from tools.logs import get_logs
from tools.metrics import get_metrics
from tools.traces import get_trace


# =========================================================
# INCIDENT AGENT (AGENTIC VERSION)
# =========================================================
class IncidentAgent:

    def __init__(self, incident: dict):
        self.incident = incident

        # INTERNAL WORKING STATE
        self.context = {
            "service": incident.get("service"),
            "alert_type": incident.get("alert_type"),
            "message": incident.get("message"),

            # investigation memory
            "metrics": None,
            "logs": None,
            "trace_data": None,

            # reasoning
            "hypothesis": None
        }

    # =====================================================
    # STEP 1: INITIAL UNDERSTANDING
    # =====================================================
    def understand(self):
        self.context["suspected_service"] = self.context["service"]

    # =====================================================
    # TOOL: FETCH METRICS
    # =====================================================
    def fetch_metrics(self):
        service = self.context["suspected_service"]

        metrics = get_metrics(service)

        self.context["metrics"] = metrics

        return metrics

    # =====================================================
    # TOOL: FETCH LOGS
    # =====================================================
    def fetch_logs(self):
        service = self.context["suspected_service"]

        logs = get_logs(service)

        self.context["logs"] = logs

        return logs

    # =====================================================
    # TOOL: FETCH TRACES
    # =====================================================
    def fetch_traces(self):
        service = self.context["suspected_service"]

        trace_data = get_trace(service)

        self.context["trace_data"] = trace_data

        return trace_data

    # =====================================================
    # AGENTIC REASONING LOOP
    # =====================================================
    def investigate(self):

        # -----------------------------------------------
        # STEP 1: START WITH METRICS
        # -----------------------------------------------
        metrics = self.fetch_metrics()

        latency = metrics.get("latency_p95", 0)
        error_rate = metrics.get("error_rate", 0)

        # -----------------------------------------------
        # STEP 2: DECIDE NEXT ACTION
        # -----------------------------------------------
        if latency > 700:

            # hypothesis from metrics
            self.context["hypothesis"] = (
                "Possible database or dependency latency issue"
            )

            # fetch logs because latency is suspicious
            logs = self.fetch_logs()

            # -------------------------------------------
            # STEP 3: REASON OVER LOGS
            # -------------------------------------------
            if any("DB" in log for log in logs):

                self.context["hypothesis"] = (
                    "Database query latency spike detected"
                )

                # traces can confirm bottleneck
                trace_data = self.fetch_traces()

                slow_spans = [
                    span for span in trace_data["spans"]
                    if span["duration_ms"] > 500
                ]

                if slow_spans:
                    self.context["hypothesis"] = (
                        "Database bottleneck confirmed via distributed traces"
                    )

            else:
                self.context["hypothesis"] = (
                    "High latency without DB evidence"
                )

        elif error_rate > 0.03:

            self.context["hypothesis"] = (
                "Elevated error rate detected"
            )

            # fetch logs for failure evidence
            self.fetch_logs()

        else:

            self.context["hypothesis"] = (
                "No major anomaly detected"
            )

    # =====================================================
    # FINAL RESULT
    # =====================================================
    def generate_result(self):

        return {
            "root_cause": self.context["hypothesis"],

            "confidence": 0.84,

            "evidence": {
                "metrics": self.context["metrics"],
                "logs": self.context["logs"],
                "trace": self.context["trace_data"]
            },

            "suggested_fix": self._suggest_fix()
        }

    # =====================================================
    # FIX SUGGESTIONS
    # =====================================================
    def _suggest_fix(self):

        hypothesis = self.context["hypothesis"]

        if "Database" in hypothesis:
            return (
                "Inspect slow DB queries and verify indexes"
            )

        if "latency" in hypothesis:
            return (
                "Investigate upstream dependencies and traffic spikes"
            )

        if "error rate" in hypothesis:
            return (
                "Inspect failing services and recent deployments"
            )

        return (
            "Collect more telemetry data"
        )

    # =====================================================
    # MAIN EXECUTION
    # =====================================================
    def run(self):

        self.understand()

        self.investigate()

        return self.generate_result()