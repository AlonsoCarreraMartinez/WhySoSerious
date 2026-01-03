from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.services.bert_inference import analyze_text
from app.database import db
from app.routers import users, teams
from app.routers import auth
from app.routers import burnout
from app.routers import channels
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from app.bot import WhySoSeriousBot
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# python -m venv .venv
# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

bot_settings = BotFrameworkAdapterSettings(os.getenv("MICROSOFT_APP_ID", ""), os.getenv("MICROSOFT_APP_PASSWORD", ""))
bot_adapter = BotFrameworkAdapter(bot_settings)
my_bot = WhySoSeriousBot()

app = FastAPI(title="WhySoSerious Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(auth.router)
app.include_router(burnout.router)
app.include_router(channels.router)

class AnalyzeRequest(BaseModel):
    text: str

class IncomingMessage(BaseModel):
    user: str
    message: str
    timestamp: datetime


class NewMessageRequest(BaseModel):
    messages: List[IncomingMessage]
    participants: List[str]


@app.get("/health")
def health_check():
    return {"status": "ok"}

#  Receive a block of messages, analyze each one with BERT and return aggregated sentiment scores.
@app.post("/new-message")
def new_message(payload: NewMessageRequest):

    analyzed_messages = []
    for msg in payload.messages:
        scores = analyze_text(msg.message)
        analyzed_messages.append({
            "user": msg.user,
            "message": msg.message,
            "timestamp": msg.timestamp,
            "scores": scores
        })

    # Aggregated scores
    avg_politeness = sum(m["scores"]["politeness"] for m in analyzed_messages) / len(analyzed_messages)
    avg_sarcasm = sum(m["scores"]["sarcasm"] for m in analyzed_messages) / len(analyzed_messages)
    avg_toxicity = sum(m["scores"]["toxicity"] for m in analyzed_messages) / len(analyzed_messages)

    block = {
        "start_time": analyzed_messages[0]["timestamp"],
        "end_time": analyzed_messages[-1]["timestamp"],
        "participants": payload.participants,
        "messages": analyzed_messages,
        "aggregated_scores": {
            "politeness": round(avg_politeness, 2),
            "sarcasm": round(avg_sarcasm, 2),
            "toxicity": round(avg_toxicity, 2)
        }
    }

    # Save to MongoDB
    result = db.message_blocks.insert_one(block)
    block["_id"] = str(result.inserted_id)

    return block

# Endpoint to connect to the emulator
@app.post("/api/messages")
async def messages(req: Request):
    if "application/json" in req.headers.get("content-type", ""):
        body = await req.json()
    else:
        return Response(status_code=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    try:
        response = await bot_adapter.process_activity(activity, auth_header, my_bot.on_turn)
        if response:
            return response
        return Response(status_code=201)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        return Response(status_code=500)
    

@app.get("/api/messages")
async def prueba_navegador():
    return "The server it's okay."

# NGROK
frontend_path = os.path.join(os.getcwd(), "..", "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f" Frontend mounted from {frontend_path}")
else:
    print("The folder doesn't found, maybe you don't execute 'npm run build'")
