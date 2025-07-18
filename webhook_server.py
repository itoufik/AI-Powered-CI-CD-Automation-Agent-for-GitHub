from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from pathlib import Path
import json
from datetime import datetime

EVENTS_FILE = Path(__file__).parent / "github_events.json"

app = FastAPI()

async def save_event(data, headers):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": headers.get("X-GitHub-Event", "unknown"),
        "action": data.get("action"),
        "workflow_run": data.get("workflow_run"),
        "check_run": data.get("check_run"),
        "repository": data.get("repository", {}).get("full_name"),
        "sender": data.get("sender", {}).get("login")
    }
    events = []
    if EVENTS_FILE.exists():
        events = json.loads(EVENTS_FILE.read_text())
    events.append(event)
    events = events[-100:]
    EVENTS_FILE.write_text(json.dumps(events, indent=2))

@app.post("/webhook/github")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    background_tasks.add_task(save_event, data, request.headers)
    return {"status": "received"}
