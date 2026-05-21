from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone


app = FastAPI(
    title="AI On-Call Automation",
    description="AI Incident Investigation Agent",
    version="0.1.0"
)

# =========================================================
# MVP IN-MEMORY INCIDENT STORE
# (Later -> Postgres + Redis)
# =========================================================
INCIDENTS = {}


# =========================================================
# ALERT PAYLOAD MODEL
# This simulates PagerDuty / Datadog / Sentry webhooks
# =========================================================
class AlertPayload(BaseModel):
    service: str
    severity: str
    alert_type: str
    message: str
    source: str


# =========================================================
# TRACE LOGGER
# =========================================================
def add_trace(incident: dict, step: str, data=None):
    incident["trace"].append({
        "step": step,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# =========================================================
# 1. ALERT INGESTION ENDPOINT
# =========================================================
@app.post("/alerts")
async def ingest_alert(payload: AlertPayload):
    """
    Receives alerts from:
    - PagerDuty
    - Datadog
    - Sentry
    - Opsgenie

    Creates an internal incident object.
    """

    incident_id = str(uuid4())

    INCIDENTS[incident_id] = {
        "id": incident_id,
        "service": payload.service,
        "severity": payload.severity,
        "alert_type": payload.alert_type,
        "message": payload.message,
        "source": payload.source,
        "status": "CREATED",
        "created_at": datetime.now(timezone.utc),
        "result": None,
        "trace": []
    }

    incident = INCIDENTS[incident_id]

    add_trace(
        incident,
        "incident_created",
        {
            "source": payload.source,
            "severity": payload.severity
        }
    )

    return {
        "message": "Incident created successfully",
        "incident_id": incident_id,
        "status": incident["status"]
    }


# =========================================================
# 2. GET INCIDENT STATE
# =========================================================
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


# =========================================================
# 3. START AI INVESTIGATION
# =========================================================
@app.post("/incidents/{incident_id}/investigate")
def investigate_incident(incident_id: str):

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if incident["status"] == "RUNNING":
        return {
            "message": "Investigation already running"
        }

    incident["status"] = "RUNNING"

    add_trace(
        incident,
        "investigation_started"
    )

    # =====================================================
    # PLACEHOLDER RESULT
    # (Later replaced with real AI agent)
    # =====================================================
    incident["result"] = {
        "root_cause": (
            "Potential database latency spike "
            "after recent deployment"
        ),
        "confidence": 0.81,
        "suggested_fix": (
            "Inspect recent DB queries and deployment changes"
        )
    }

    incident["status"] = "COMPLETED"

    add_trace(
        incident,
        "investigation_completed",
        incident["result"]
    )

    return {
        "message": "Investigation completed",
        "incident_id": incident_id,
        "status": incident["status"]
    }


# =========================================================
# 4. INCIDENT TRACE / OBSERVABILITY
# =========================================================
@app.get("/incidents/{incident_id}/trace")
def get_incident_trace(incident_id: str):

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return {
        "incident_id": incident_id,
        "status": incident["status"],
        "trace": incident["trace"]
    }