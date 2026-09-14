import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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


class ExecutiveChatResponse(BaseModel):
    response: str
    specialists_used: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ── API routes ────────────────────────────────────────────────────────────────
@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/briefing", response_model=BriefingResponse)
@app.post("/briefing", response_model=BriefingResponse)
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


@app.post("/api/chat/executive", response_model=ExecutiveChatResponse)
@app.post("/chat/executive", response_model=ExecutiveChatResponse)
def chat_executive(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    from executive_agent import run_executive_turn
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
    try:
        return run_executive_turn(request.message, history=history_dicts)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Executive Chief of Staff failed: {str(e)}",
        )


@app.post("/api/chat/{specialist}")
@app.post("/chat/{specialist}")
def chat_specialist(specialist: str, request: ChatRequest):
    spec = specialist.lower().strip()
    if spec == "executive":
        return chat_executive(request)

    if spec not in ("finance", "ops", "marketing"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown specialist '{specialist}'. Valid options: executive, finance, ops, marketing.",
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


# ── Static file & SPA serving ────────────────────────────────────────────────
_FRONTEND_DIST = Path(_PROJECT_ROOT) / "frontend" / "dist"
_ASSETS_DIR = _FRONTEND_DIST / "assets"

if _ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(_ASSETS_DIR)),
        name="assets",
    )


@app.get("/", include_in_schema=False)
async def serve_root():
    index_file = _FRONTEND_DIST / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    return HTMLResponse(
        "<!DOCTYPE html><html><head><title>AGentic Resolve</title></head>"
        "<body style='font-family:sans-serif;padding:2rem;background:#0f172a;color:#f8fafc;'>"
        "<h2>Frontend build not found</h2>"
        "<p>React frontend index.html not found. Run <code>npm run build</code> in the frontend directory.</p>"
        "</body></html>"
    )


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str, request: Request):
    """Serve the React SPA for any non-API route."""
    clean_path = full_path.strip("/")
    # Never intercept API routes
    if clean_path.startswith("api") or clean_path in ("health", "docs", "redoc", "openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Try exact static file in frontend/dist (e.g. vite.svg, favicon.ico, etc.)
    requested = _FRONTEND_DIST / clean_path
    if requested.is_file():
        return FileResponse(str(requested))

    # Fall back to index.html so React Router handles the route client-side (/briefing, /chat/..., etc.)
    index_file = _FRONTEND_DIST / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))

    return HTMLResponse(
        "<!DOCTYPE html><html><head><title>AGentic Resolve</title></head>"
        "<body style='font-family:sans-serif;padding:2rem;background:#0f172a;color:#f8fafc;'>"
        "<h2>Page Not Found</h2>"
        "<p>React frontend index.html not found. Run <code>npm run build</code> in the frontend directory.</p>"
        "</body></html>"
    )
