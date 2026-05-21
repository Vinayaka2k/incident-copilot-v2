from datetime import datetime, timezone
from tools.logs import get_logs
from tools.metrics import get_metrics
from tools.traces import get_trace


# =========================================================
# INCIDENT AGENT
# =========================================================

class IncidentAgent:

    def __init__(self, incident: dict):
        self.incident = incident
        self.trace = incident["trace"]

        self.context = {
            "service": incident.get("service"),
            "alert_type": incident.get("alert_type"),
            "message": incident.get("message"),
        }

    # -----------------------------------------------------
    # TRACE LOGGER
    # -----------------------------------------------------
    def log(self, step: str, data=None):
        self.trace.append({
            "step": step,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # -----------------------------------------------------
    # STEP 1: UNDERSTAND INCIDENT
    # -----------------------------------------------------
    def understand(self):
        self.log("understand_incident")

        # ✔ FIXED: no redundant condition
        # For now, service comes directly from alert payload
        self.context["suspected_service"] = self.context["service"]

    # -----------------------------------------------------
    # STEP 2: COLLECT DATA
    # -----------------------------------------------------
    def collect_data(self):
        service = self.context["suspected_service"]

        self.log("fetch_logs", {"service": service})
        logs = get_logs(service)

        self.log("fetch_metrics", {"service": service})
        metrics = get_metrics(service)

        self.log("fetch_trace", {"service": service})
        trace_data = get_trace(service)

        self.context.update({
            "logs": logs,
            "metrics": metrics,
            "trace_data": trace_data
        })

    # -----------------------------------------------------
    # STEP 3: ANALYZE DATA
    # -----------------------------------------------------
    def analyze(self):
        self.log("analyze_incident")

        metrics = self.context["metrics"]
        logs = self.context["logs"]

        if metrics["latency_p95"] > 700:
            if any("DB" in log for log in logs):
                self.context["hypothesis"] = (
                    "Database query inefficiency or missing index"
                )
            else:
                self.context["hypothesis"] = (
                    "High latency from non-DB component"
                )
        else:
            self.context["hypothesis"] = "No clear anomaly detected"

    # -----------------------------------------------------
    # STEP 4: GENERATE RESULT
    # -----------------------------------------------------
    def generate_result(self):
        self.log("generate_result")

        result = {
            "root_cause": self.context["hypothesis"],
            "confidence": 0.82,
            "evidence": {
                "logs": self.context["logs"],
                "metrics": self.context["metrics"],
                "trace": self.context["trace_data"]
            },
            "suggested_fix": "Investigate DB indexes and recent deployments"
        }

        self.incident["result"] = result
        self.incident["status"] = "COMPLETED"

        self.log("analysis_completed", result)

        return result

    # -----------------------------------------------------
    # MAIN EXECUTION LOOP
    # -----------------------------------------------------
    def run(self):
        self.log("agent_started")

        self.understand()
        self.collect_data()
        self.analyze()

        return self.generate_result()