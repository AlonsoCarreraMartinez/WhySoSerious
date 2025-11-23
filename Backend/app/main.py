from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.services.bert_inference import analyze_text
from app.database import db
from app.routers import users, teams
from app.routers import auth
from app.routers import burnout

# python -m venv .venv
# uvicorn app.main:app --reload
#http://127.0.0.1:8000/docs

app = FastAPI(title="WhySoSerious Backend")

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(auth.router)
app.include_router(burnout.router)

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
