import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ── Project root on sys.path ────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from orchestrator import run_briefing_structured
from agents.finance_agent import run_finance_query
from agents.ops_agent import run_ops_query
from agents.marketing_agent import run_marketing_query

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AGentic Resolve API",
    description="Multi-agent executive assistant powered by Strands Agents SDK",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# In production the frontend is served from the same origin by FastAPI itself,
# so CORS is only needed for local dev (http://localhost:5173).
_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ───────────────────────────────────────────────────────────
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
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation history",
    )


class ChatResponse(BaseModel):
    response: str


# ── API routes ────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


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
            detail=f"Unknown specialist '{specialist}'. Valid options: finance, ops, marketing.",
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


# ── Static file serving (production SPA) ─────────────────────────────────────
# Mount the built React app. FastAPI serves /assets/* etc. directly.
# Any unknown route falls through to index.html for React Router.
_FRONTEND_DIST = Path(_PROJECT_ROOT) / "frontend" / "dist"

if _FRONTEND_DIST.exists():
    # Serve static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=str(_FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str, request: Request):
        """Serve the React SPA for any non-API route."""
        # Try to serve an exact file first (favicon.ico, robots.txt, etc.)
        requested = _FRONTEND_DIST / full_path
        if requested.is_file():
            return FileResponse(str(requested))
        # Fall back to index.html so React Router can handle the route client-side
        return FileResponse(str(_FRONTEND_DIST / "index.html"))
