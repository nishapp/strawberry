import os
import base64
import json
import logging
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events import Event, RequestInput

# Configure standard Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("strawberry_web")

from strawberry_agent.agent import app as adk_app

app = FastAPI(title="Strawberry Agent Gateway")

# Enable CORS (allow all for local development flexibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = Runner(
    app=adk_app,
    session_service=session_service,
    artifact_service=artifact_service,
    auto_create_session=True  # Automatically create session so frontend direct runs work!
)

class RunRequest(BaseModel):
    app_name: Optional[str] = None
    user_id: str
    session_id: str
    new_message: dict

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # Read index.html from root directory and serve it
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="index.html not found")

@app.post("/apps/{app_name}/users/{user_id}/sessions")
async def create_session(app_name: str, user_id: str, req: dict):
    session_id = req.get("session_id")
    session = await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    return {"id": session.id}

@app.post("/run")
async def run_agent(req: RunRequest):
    # Parse new_message Content
    msg_data = req.new_message
    role = msg_data.get("role", "user")
    parts_data = msg_data.get("parts", [])
    
    parts = []
    for p in parts_data:
        if "text" in p:
            parts.append(types.Part(text=p["text"]))
        elif "function_response" in p:
            fr = p["function_response"]
            parts.append(types.Part(
                function_response=types.FunctionResponse(
                    id=fr["id"],
                    name=fr["name"],
                    response=fr["response"]
                )
            ))
            
    content = types.Content(role=role, parts=parts)
    
    events = []
    async for event in runner.run_async(
        user_id=req.user_id,
        session_id=req.session_id,
        new_message=content
    ):
        events.append(event)
        
    return events

# Pub/Sub Push endpoint
class PubSubMessage(BaseModel):
    message: dict

@app.post("/pubsub")
@app.post("/trigger/pubsub")
async def pubsub_trigger(req: PubSubMessage):
    logger.info("Received Pub/Sub message trigger")
    try:
        # Extract base64 payload
        data_b64 = req.message.get("data")
        if not data_b64:
            raise HTTPException(status_code=400, detail="Missing data field in Pub/Sub message")
            
        # Decode base64
        decoded_bytes = base64.b64decode(data_b64)
        decoded_str = decoded_bytes.decode("utf-8")
        
        # Parse payload as JSON or string
        session_id = "pubsub_session"
        user_id = "pubsub_user"
        text_message = ""
        
        try:
            payload = json.loads(decoded_str)
            if isinstance(payload, dict):
                text_message = payload.get("text") or payload.get("message") or decoded_str
                session_id = payload.get("session_id") or session_id
                user_id = payload.get("user_id") or user_id
            else:
                text_message = decoded_str
        except json.JSONDecodeError:
            text_message = decoded_str
            
        logger.info(f"Processing Pub/Sub event: User ID={user_id}, Session ID={session_id}, Message={text_message}")
        
        # Run agent runner
        content = types.Content(role="user", parts=[types.Part(text=text_message)])
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            events.append(event)
            
        # Extract response text
        response_text = ""
        for event in events:
            if event.output:
                if isinstance(event.output, dict):
                    response_text = event.output.get("response") or response_text
                else:
                    response_text = getattr(event.output, "response", response_text)
                    
        logger.info(f"Agent response to Pub/Sub: {response_text}")
        return {"status": "success", "response": response_text}
        
    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
