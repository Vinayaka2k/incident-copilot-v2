from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone

app = FastAPI(
    title="AI Incident Copilot MVP",
    description="Slack-first AI system for incident debugging",
    version="0.1.0"
)

# -----------------------------
# IN-MEMORY STORAGE (MVP ONLY)
# -----------------------------
INCIDENTS = {}


# -----------------------------
# MODELS
# -----------------------------
class SlackIncidentRequest(BaseModel):
    text: str
    user: str | None = None


# -----------------------------
# HELPERS
# -----------------------------
def add_trace(incident: dict, step: str):
    """Utility to log execution steps for observability"""
    incident["trace"].append({
        "step": step,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# -----------------------------
# 1. SLACK ENTRYPOINT
# -----------------------------
@app.post("/slack/incident")
async def slack_incident(payload: SlackIncidentRequest):
    """
    Slack sends incident → we create internal incident object
    """

    incident_id = str(uuid4())

    INCIDENTS[incident_id] = {
        "id": incident_id,
        "description": payload.text,
        "created_by": payload.user,
        "created_at": datetime.now(timezone.utc),
        "status": "CREATED",
        "result": None,
        "trace": []
    }

    incident = INCIDENTS[incident_id]
    add_trace(incident, "incident_created")

    return {
        "message": "Incident received",
        "incident_id": incident_id,
        "status": "CREATED"
    }


# -----------------------------
# 2. GET INCIDENT STATE
# -----------------------------
@app.get("/incident/{incident_id}")
def get_incident(incident_id: str):
    """
    Fetch current state of a single incident
    """

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


# -----------------------------
# 3. ANALYZE INCIDENT (MVP PLACEHOLDER)
# -----------------------------
@app.post("/incident/{incident_id}/analyze")
def analyze_incident(incident_id: str):
    """
    Triggers AI analysis pipeline (currently mocked)
    """

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident["status"] == "RUNNING":
        return {"message": "Already running"}

    incident["status"] = "RUNNING"
    add_trace(incident, "analysis_started")

    # -------------------------
    # MOCK AI RESULT (TEMPORARY)
    # -------------------------
    incident["result"] = {
        "root_cause": "Database latency spike due to missing index",
        "confidence": 0.72,
        "suggestion": "Add index on user_id column"
    }

    add_trace(incident, "analysis_completed")
    incident["status"] = "COMPLETED"

    return {
        "message": "Analysis complete",
        "incident_id": incident_id
    }


# -----------------------------
# 4. TRACE ENDPOINT (OBSERVABILITY)
# -----------------------------
@app.get("/incident/{incident_id}/trace")
def get_trace(incident_id: str):
    """
    Returns step-by-step execution history
    """

    incident = INCIDENTS.get(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident_id,
        "trace": incident["trace"],
        "status": incident["status"]
    }