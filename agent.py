from tools.logs import get_logs
from tools.metrics import get_metrics
from tools.traces import get_trace


# =========================================================
# INCIDENT AGENT (PURE LOGIC ENGINE)
# =========================================================
class IncidentAgent:

    def __init__(self, incident: dict):
        # snapshot only (DO NOT MUTATE INCIDENT)
        self.incident = incident

        self.context = {
            "service": incident.get("service"),
            "alert_type": incident.get("alert_type"),
            "message": incident.get("message"),
        }

    # =====================================================
    # STEP 1: UNDERSTAND INCIDENT
    # =====================================================
    def understand(self):
        service = self.context["service"]

        self.context["suspected_service"] = service

    # =====================================================
    # STEP 2: COLLECT DATA FROM TOOLS
    # =====================================================
    def collect_data(self):
        service = self.context["suspected_service"]

        logs = get_logs(service)
        metrics = get_metrics(service)
        trace_data = get_trace(service)

        self.context.update({
            "logs": logs,
            "metrics": metrics,
            "trace_data": trace_data
        })

    # =====================================================
    # STEP 3: ANALYZE INCIDENT (RULE-BASED MVP LOGIC)
    # =====================================================
    def analyze(self):
        metrics = self.context["metrics"]
        logs = self.context["logs"]

        latency = metrics.get("latency_p95", 0)

        # simple deterministic hypothesis logic (MVP-safe)
        if latency > 700:
            if any("DB" in log for log in logs):
                hypothesis = "Database query latency spike (possible missing index or slow query)"
            else:
                hypothesis = "High latency due to non-database service bottleneck"
        elif metrics.get("error_rate", 0) > 0.03:
            hypothesis = "Increased error rate indicating failing dependency or upstream outage"
        else:
            hypothesis = "No clear anomaly detected from available signals"

        self.context["hypothesis"] = hypothesis

    # =====================================================
    # STEP 4: GENERATE FINAL RESULT (NO SIDE EFFECTS)
    # =====================================================
    def generate_result(self):
        return {
            "root_cause": self.context["hypothesis"],
            "confidence": 0.80,  # static MVP confidence (LLM later will replace this)
            "evidence": {
                "logs": self.context.get("logs", []),
                "metrics": self.context.get("metrics", {}),
                "trace": self.context.get("trace_data", {})
            },
            "suggested_fix": self._suggest_fix()
        }

    # =====================================================
    # SIMPLE RULE-BASED FIX SUGGESTION (MVP)
    # =====================================================
    def _suggest_fix(self):
        hypothesis = self.context.get("hypothesis", "")

        if "Database" in hypothesis:
            return "Check recent deployments and add/verify DB indexes for slow queries"
        if "latency" in hypothesis:
            return "Investigate service dependency bottlenecks and recent traffic spikes"
        if "error rate" in hypothesis:
            return "Check upstream dependency failures and recent code changes"

        return "Collect more observability data and re-run investigation"

    # =====================================================
    # MAIN PIPELINE (PURE FUNCTION STYLE)
    # =====================================================
    def run(self):
        self.understand()
        self.collect_data()
        self.analyze()
        return self.generate_result()