from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
import json
from datetime import datetime
import httpx

app = FastAPI()

# Use environment variable for local storage path
EVENTS_FILE = Path(__file__).parent / "github_events.json"
LOCAL_WEBHOOK_URL = "http://localhost:8000/local-events"  # Your local server URL

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
    return event

async def send_to_local(event):
    """Send event to local server for logging"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(LOCAL_WEBHOOK_URL, json=event)
    except Exception as e:
        print(f"Failed to send to local server: {e}")

@app.post("/webhook/github")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    event = await save_event(data, request.headers)
    
    # Send to local server asynchronously
    await send_to_local(event)
    
    return {"status": "received"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
