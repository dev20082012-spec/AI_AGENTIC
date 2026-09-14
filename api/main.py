import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from orchestrator import run_briefing_structured
from agents.finance_agent import run_finance_query
from agents.ops_agent import run_ops_query
from agents.marketing_agent import run_marketing_query

app = FastAPI(
    title="AGentic Resolve API",
    description="Multi-agent executive assistant powered by Strands Agents SDK",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BriefingRequest(BaseModel):
    query: str = Field(..., description="Business question or briefing request")


class SpecialistDetail(BaseModel):
    called: bool
    summary: str


class BriefingResponse(BaseModel):
    query: str
    specialists_called: list[str]
    specialist_results: dict[str, SpecialistDetail]
    synthesized_briefing: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the specialist")
    history: list[ChatMessage] = Field(default_factory=list, description="Prior conversation history")


class ChatResponse(BaseModel):
    response: str


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/briefing", response_model=BriefingResponse)
def get_briefing(request: BriefingRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        data = run_briefing_structured(request.query)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent orchestration failed: {str(e)}",
        )


@app.post("/api/chat/{specialist}", response_model=ChatResponse)
def chat_specialist(specialist: str, request: ChatRequest):
    spec = specialist.lower().strip()
    if spec not in ("finance", "ops", "marketing"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown specialist '{specialist}'. Supported: 'finance', 'ops', 'marketing'.",
        )
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
    try:
        if spec == "finance":
            ans = run_finance_query(request.message, history=history_dicts)
        elif spec == "ops":
            ans = run_ops_query(request.message, history=history_dicts)
        elif spec == "marketing":
            ans = run_marketing_query(request.message, history=history_dicts)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"{specialist.capitalize()} specialist failed: {str(e)}",
        )
