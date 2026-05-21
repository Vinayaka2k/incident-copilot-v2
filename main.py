from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone

from agent import IncidentAgent

app = FastAPI(
    title="AI On-Call Automation",
    description="AI Incident Investigation Agent",
    version="0.1.0"
)

# =========================================================
# IN-MEMORY INCIDENT STORE (MVP ONLY)
# =========================================================
INCIDENTS = {}


# =========================================================
# ALERT PAYLOAD MODEL (PagerDuty / Datadog / Sentry)
# =========================================================
class AlertPayload(BaseModel):
    service: str
    severity: str
    alert_type: str
    message: str
    source: str


# =========================================================
# TRACE LOGGER (ONLY main.py OWNS TRACE)
# =========================================================
def add_trace(incident: dict, step: str, data=None):
    incident["trace"].append({
        "step": step,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# =========================================================
# 1. ALERT INGESTION
# =========================================================
@app.post("/alerts")
async def ingest_alert(payload: AlertPayload):
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

        # result will be filled after investigation
        "result": None,

        # trace is owned ONLY here
        "trace": []
    }

    incident = INCIDENTS[incident_id]

    add_trace(incident, "incident_created", {
        "source": payload.source,
        "severity": payload.severity
    })

    return {
        "message": "Incident created successfully",
        "incident_id": incident_id,
        "status": incident["status"]
    }


# =========================================================
# 2. GET INCIDENT
# =========================================================
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


# =========================================================
# 3. RUN INVESTIGATION (SYNCHRONOUS MVP FLOW)
# =========================================================
@app.post("/incidents/{incident_id}/investigate")
def investigate_incident(incident_id: str):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident["status"] == "RUNNING":
        return {"message": "Investigation already running"}

    # STEP 1: mark running (ONLY main.py changes state)
    incident["status"] = "RUNNING"
    add_trace(incident, "investigation_started")

    # STEP 2: run pure agent
    agent = IncidentAgent(incident)
    result = agent.run()

    # STEP 3: apply result (ONLY main.py mutates incident)
    incident["result"] = result
    incident["status"] = "COMPLETED"

    add_trace(incident, "investigation_completed", result)

    return {
        "message": "Investigation completed",
        "incident_id": incident_id,
        "status": incident["status"]
    }


# =========================================================
# 4. TRACE VIEWER
# =========================================================
@app.get("/incidents/{incident_id}/trace")
def get_incident_trace(incident_id: str):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident_id,
        "status": incident["status"],
        "trace": incident["trace"]
    }