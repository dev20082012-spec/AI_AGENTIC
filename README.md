# AGentic Resolve — Multi-Agent Executive AI

A production-ready AI Chief of Staff application built with the **Strands Agents SDK**, **FastAPI**, and **React**. Three specialist agents (Finance, Operations, Marketing) run in parallel and synthesize enterprise intelligence into executive briefings.

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Single FastAPI Process         │
│   (serves API + built React frontend)    │
│                                         │
│  POST /api/chat/{specialist}  ──►  Groq │
│  POST /api/briefing            ──►  Orchestrator │
│  GET  /                       ──►  React SPA     │
└─────────────────────────────────────────┘
```

**Stack:**
- **Backend**: FastAPI + Strands Agents SDK + Groq (qwen/qwen3.8-27b)
- **Frontend**: React 19 + React Router + Tailwind CSS
- **Data**: Pre-aggregated pandas/numpy analytics from local CSV/JSON fixtures
- **Deployment**: Single process — FastAPI serves both the API and the built React app

---

## 🚀 Quick Start (Local Dev)

### 1. Clone & Set Up Environment

```bash
git clone <your-repo-url>
cd AI_AGENTIC

# Create a .env file with your Groq API key
cp .env.example .env
# Edit .env and set: GROQ_API_KEY=your_key_here
```

Get a free Groq key at: https://console.groq.com → API Keys

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install & Run Frontend (Dev Mode)

```bash
cd frontend
npm install
npm run dev       # Frontend dev server on http://localhost:5173
cd ..
```

### 4. Run the Backend

```bash
uvicorn api.main:app --reload --port 8000
```

- **Frontend (dev)**: http://localhost:5173
- **API docs**: http://localhost:8000/api/docs

---

## 🌐 Production Deployment

In production, FastAPI **serves both the API and the built React frontend** from a single process on a single port. No Vite dev server is needed.

### Deploy to Render.com (Free Tier — Recommended)

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → Connect your repo.
3. Render detects `render.yaml` automatically.
4. In the Render dashboard → **Environment** tab, add:
   ```
   GROQ_API_KEY = your_groq_api_key_here
   ```
5. Click **Deploy**. Render will:
   - Install Python deps (`pip install -r requirements.txt`)
   - Build the React frontend (`cd frontend && npm install && npm run build`)
   - Start FastAPI (`uvicorn api.main:app --host 0.0.0.0 --port $PORT`)
6. Your app is live at `https://your-app.onrender.com`.

### Deploy to Railway.app

1. Push to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → Deploy from GitHub repo.
3. Add environment variable: `GROQ_API_KEY = your_key_here`
4. Add a start command in the service settings:
   ```
   pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
5. Deploy — your app is live at `https://your-app.up.railway.app`.

### Deploy to Any VPS / Cloud (AWS EC2, DigitalOcean, Fly.io)

```bash
# On the server:
git clone <your-repo>
cd AI_AGENTIC

# Set environment variable
export GROQ_API_KEY=your_key_here

# Install Python deps
pip install -r requirements.txt

# Build frontend + start server (one command)
bash startup.sh
```

Or with a process manager (recommended for production):
```bash
pip install gunicorn
gunicorn api.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq Cloud API key (free at console.groq.com) |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins (default: localhost only) |
| `PORT` | No | Port to listen on (default: 8000, set automatically by hosting platforms) |

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/chat/{specialist}` | POST | Multi-turn chat with finance / ops / marketing |
| `/api/briefing` | POST | Full orchestrator briefing across all 3 specialists |
| `/api/docs` | GET | Interactive Swagger UI |

### Chat Request Example

```bash
curl -X POST https://your-app.com/api/chat/finance \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our revenue trend?", "history": []}'
```

### Briefing Request Example

```bash
curl -X POST https://your-app.com/api/briefing \
  -H "Content-Type: application/json" \
  -d '{"query": "Give me this weeks executive briefing"}'
```

---

## Project Structure

```
AI_AGENTIC/
├── api/
│   └── main.py              # FastAPI app (serves API + React SPA)
├── agents/
│   ├── finance_agent.py     # Revenue analytics agent
│   ├── ops_agent.py         # Operations management agent
│   └── marketing_agent.py   # Campaign analytics agent
├── data/
│   ├── sales_sample.csv     # Finance data
│   ├── employee_updates.json # Ops data
│   └── campaign_sample.csv  # Marketing data
├── frontend/
│   ├── src/
│   │   ├── config.js        # API base URL (relative in prod, localhost in dev)
│   │   ├── context/
│   │   │   └── ChatContext.jsx  # localStorage-persisted conversation history
│   │   └── pages/
│   │       ├── LandingPage.jsx  # 4-card Executive Hub
│   │       ├── ChatPage.jsx     # Per-specialist multi-turn chat
│   │       └── BriefingPage.jsx # Full orchestrator briefing
│   └── dist/                # Built by `npm run build` — served by FastAPI
├── model.py                 # LLM config (Groq / AWS Bedrock)
├── orchestrator.py          # Chief of Staff orchestrator agent
├── requirements.txt         # Python dependencies
├── render.yaml              # Render.com deployment config
├── railway.toml             # Railway.app deployment config
├── Procfile                 # Heroku/generic Procfile
├── startup.sh               # Universal startup script
└── .env.example             # Environment variable template
```

---

## Built With

- [Strands Agents SDK](https://github.com/strands-agents/sdk-python) — Multi-agent orchestration framework
- [Groq](https://console.groq.com) — Ultra-fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com) — Production Python API server
- [React 19](https://react.dev) + [React Router](https://reactrouter.com) — Frontend SPA
- [Tailwind CSS](https://tailwindcss.com) — Utility-first styling
