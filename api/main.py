import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root workspace directory is in sys.path so we can import orchestrator
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from orchestrator import run_briefing_structured

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


class SpecialistResults(BaseModel):
    finance: SpecialistDetail
    ops: SpecialistDetail
    marketing: SpecialistDetail


class BriefingResponse(BaseModel):
    query: str
    specialists_called: list[str]
    specialist_results: dict[str, SpecialistDetail]
    synthesized_briefing: str


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
