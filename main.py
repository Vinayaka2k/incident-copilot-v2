from fastapi import FastAPI, HTTPException, BackgroundTasks
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
# IN-MEMORY STORE
# =========================================================
INCIDENTS = {}


# =========================================================
# ALERT MODEL
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
# BACKGROUND WORKER (THIS IS WHERE AGENT RUNS)
# =========================================================
def run_investigation(incident_id: str):
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return

    try:
        # mark running
        incident["status"] = "RUNNING"
        add_trace(incident, "investigation_started")

        # run agent (pure logic)
        agent = IncidentAgent(incident)
        result = agent.run()

        # store result
        incident["result"] = result
        incident["status"] = "COMPLETED"

        add_trace(incident, "investigation_completed", result)

    except Exception as e:
        incident["status"] = "FAILED"
        add_trace(incident, "investigation_failed", str(e))


# =========================================================
# 1. INGEST ALERT
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

        "result": None,
        "trace": []
    }

    incident = INCIDENTS[incident_id]
    add_trace(incident, "incident_created")

    return {
        "message": "Incident created",
        "incident_id": incident_id,
        "status": incident["status"]
    }


# =========================================================
# 2. START INVESTIGATION (ASYNC)
# =========================================================
@app.post("/incidents/{incident_id}/investigate")
async def investigate_incident(incident_id: str, background_tasks: BackgroundTasks):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident["status"] == "RUNNING":
        return {"message": "Already running"}

    # enqueue background job
    background_tasks.add_task(run_investigation, incident_id)

    return {
        "message": "Investigation started in background",
        "incident_id": incident_id,
        "status": "RUNNING"
    }


# =========================================================
# 3. GET INCIDENT
# =========================================================
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


# =========================================================
# 4. TRACE
# =========================================================
@app.get("/incidents/{incident_id}/trace")
def get_trace(incident_id: str):
    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident_id,
        "trace": incident["trace"]
    }