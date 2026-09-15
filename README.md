# AGentic Resolve

> **Ask your business. AGentic Resolve coordinates the answer.**

AGentic Resolve is a conversational AI Chief of Staff for business teams. Instead of forcing leaders to navigate separate analytics dashboards, it accepts natural-language questions and coordinates specialized Finance, Operations, and Marketing agents to produce grounded, decision-ready answers.

---

## Why It Exists

Business data is fragmented across revenue, delivery, and marketing operations. A single generic chatbot can summarize information, but it often lacks the domain context and tool discipline needed for reliable business analysis.

AGentic Resolve uses a multi-agent design: a top-level Executive Agent interprets the conversation, routes only the specialists that are relevant, combines their findings when a question crosses domains, and keeps the response grounded in the underlying business data.

---

## Core Experience

### Executive Chat
The flagship experience is an interactive multi-turn Executive Chief of Staff.

```
User
  │
  ▼
Executive Agent
  │
  ▼
Intent + Conversation Context
  │
  ▼
Finance / Operations / Marketing Specialist(s)
  │
  ▼
Grounded Analytics + Tool Results
  │
  ▼
Executive Synthesis
  │
  ▼
Context-Aware Response
```

The agent is designed to handle follow-ups such as:
> **"How are sales performing?"** → **"Why?"** → **"Which product is responsible?"** → **"Could operations be contributing?"** → **"What should I focus on this week?"**

It does **not** regenerate the same baseline report on every turn; the current request and recent conversation context determine what work is relevant.

### Full Business Briefing
`/api/briefing` remains a dedicated executive-report workflow for a complete Finance + Operations + Marketing business briefing. It is intentionally separate from conversational chat.

The briefing UI presents:
- Specialist consultation status
- Key findings
- Risks and opportunities
- Executive synthesis
- Top actions

Partial specialist failures are surfaced honestly rather than hidden or replaced with fabricated data.

---

## Multi-Agent Architecture

AGentic Resolve uses the **agents-as-tools** pattern: a coordinating agent can call specialized agents that have focused prompts and domain tools. This is a standard [Strands Agents pattern](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/) for hierarchical delegation and separation of concerns.

```
┌─────────────────────────────────────────┐
│                  USER                   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│             React Frontend              │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│               FastAPI API               │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│             Executive Agent             │
│          (Context + Routing)            │
└──────┬─────────────┬─────────────┬──────┘
       │             │             │
       ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Finance Agent │ │  Ops Agent   │ │Marketing Agt │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
               Executive Synthesis
```

### Specialists

| Agent | Focus | Current Data |
|---|---|---|
| **Finance** | Revenue trends, product performance, forecasts, anomalies | `data/sales_sample.csv` |
| **Operations** | Team status, blockers, stale work, scheduling | `data/employee_updates.json` |
| **Marketing** | Campaign performance, conversion, segments, market impact | `data/campaign_sample.csv` |

The specialist layer remains grounded in deterministic analytics. LLMs are used to interpret, reason over, and communicate the results rather than invent business numbers.

---

## Model Layer

The application uses a provider abstraction so the agent layer does not need to know which inference vendor is active.

```
Agent / Specialist
       │
       ▼
chat_completion()
       │
       ▼
┌──────────────┐
│   Provider   │
│    Router    │
└──────┬───────┘
       ├── Groq (Primary)
       └── OpenRouter (Fallback)
```

[OpenRouter model-level failover](https://openrouter.ai/docs/guides/routing/model-fallbacks) is supported by accepting an ordered models list and falling back when an earlier model is unavailable or rate-limited.

---

## Tool-Ready Architecture

Tools are first-class capabilities of the agent layer. Strands supports custom tools, structured outputs, streaming, MCP, agent-as-tool composition, and other production-oriented agent patterns ([Strands Tools Documentation](https://strandsagents.com/docs/user-guide/concepts/tools/) | [Strands Overview](https://strandsagents.com/docs/user-guide/quickstart/overview/)).

The roadmap for AGentic Resolve is intentionally tool-oriented:

| Phase | Capabilities |
|---|---|
| **Current** | Finance / Ops / Marketing analytics |
| **Next** | Web research, Document retrieval, CRM / database tools, Calendar / email tools, MCP-connected resources, A2A-connected remote specialists |

Strands also supports [remote A2A agents as tools](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agent-to-agent/), keeping the current specialists compatible with a future distributed architecture without requiring that complexity today.

---

## Frontend UX Direction

The product is intentionally designed as an executive operating surface rather than a generic chat screen:
- **Executive Chat is the primary workflow.**
- Specialist activity is visible at a safe summary level (e.g. `CONSULTED: Finance Specialist` badges).
- Briefings look like structured executive reports, not raw API payloads.
- Loading states clearly explain what the system is doing.
- Failed providers expose a clean, useful retry/fallback state.
- Conversation history remains easy to inspect and clear.
- Follow-up actions allow seamlessly pivoting from a briefing into active conversation.
- **Hidden chain-of-thought is never exposed.** User-facing activity describes execution status rather than internal model reasoning.

---

## Project Structure

```
AI_AGENTIC/
├── api/
│   ├── main.py                  # FastAPI application & route endpoints
│   └── index.py                 # Serverless adapter entrypoint
├── agents/
│   ├── finance_agent.py         # Revenue & financial analytics agent
│   ├── ops_agent.py             # Operations, teams & blocker agent
│   ├── marketing_agent.py       # Campaign & acquisition analytics agent
│   └── tools.py                 # MCP-ready tool registry & AgentTool protocols
├── data/
│   ├── sales_sample.csv         # Finance dataset fixture
│   ├── employee_updates.json    # Ops dataset fixture
│   └── campaign_sample.csv      # Marketing dataset fixture
├── executive_agent.py           # Multi-turn conversational Chief of Staff
├── orchestrator.py              # Fixed full briefing orchestrator
├── model.py                     # Provider abstraction (Groq + OpenRouter)
├── frontend/
│   ├── src/
│   │   ├── config.js            # API base URL configuration
│   │   ├── context/
│   │   │   └── ChatContext.jsx  # Chat state & concurrency fence
│   │   └── pages/
│   │       ├── LandingPage.jsx  # Flagship hub
│   │       ├── ChatPage.jsx     # Multi-turn conversational UI
│   │       └── BriefingPage.jsx # Full multi-specialist briefing
│   └── dist/                    # Built production assets served by FastAPI
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment configuration
├── railway.toml                 # Railway deployment configuration
├── Procfile                     # Process file for PaaS deployments
├── ARCHITECTURE.md              # Detailed technical specification
└── README.md                    # Project documentation
```

---

## Local Setup

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Set server-side environment variables in `.env`:

```env
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
PRIMARY_PROVIDER=groq
PRIMARY_MODEL=qwen/qwen3.8-27b
FALLBACK_PROVIDER=openrouter
FALLBACK_MODEL=poolside/laguna-s-2.1:free
```

> **Note**: Never commit `.env` files or expose API keys to the browser.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Run Backend Server

```bash
uvicorn api.main:app --reload --port 8000
```

- **Executive Chat**: http://localhost:8000/chat/executive
- **Executive Briefing**: http://localhost:8000/briefing
- **API Documentation**: http://localhost:8000/api/docs

---

## Production Deployment

The deployment model is a single FastAPI backend serving the built React application from one unified service.

### Deploy to Render:
1. Connect the repository in [Render Dashboard](https://dashboard.render.com).
2. Set `GROQ_API_KEY` (and `OPENROUTER_API_KEY` when OpenRouter fallback is enabled).
3. Set model/provider environment variables as needed.
4. Render executes the build command (`cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt`).
5. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
6. Verify `/api/health` before opening the public application.

---

## API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | `GET` | Service health check |
| `/api/chat/{specialist}` | `POST` | Direct domain specialist chat (finance / ops / marketing) |
| `/api/chat/executive` | `POST` | Dynamic conversational Executive Chief of Staff |
| `/api/chat/executive/stream` | `POST` | Server-Sent Events (SSE) streaming chat with status events |
| `/api/briefing` | `POST` | Complete cross-domain business briefing |
| `/api/observability` | `GET` | Real-time telemetry, provider distribution & execution traces |
| `/api/threads` | `GET`, `POST` | Server-side thread listing and persistence |
| `/api/threads/{id}` | `GET`, `DELETE`| Thread retrieval and deletion |
| `/api/docs` | `GET` | Swagger / OpenAPI documentation |

### Example Executive Chat Request

```json
POST /api/chat/executive
{
  "message": "Could operations be contributing to the sales decline?",
  "history": [
    { "role": "user", "content": "How are sales performing?" },
    { "role": "assistant", "content": "Sales are performing strongly across both product lines..." }
  ]
}
```

### Example Briefing Request

```json
POST /api/briefing
{
  "query": "Give me this week's executive briefing: revenue trend, pending ops items, and campaign performance."
}
```

---

## Testing & Verification

The most important test is not a single prompt, but conversational threads:

1. **Multi-turn Context Thread**:
   - `"How are sales performing?"`
   - `"Why?"`
   - `"Which product is responsible?"`
   - `"Could operations be contributing?"`
   - `"What should I do about it?"`
2. **Topic Switching**:
   - `"Tell me about marketing."`
   - `"Forget that. Which tasks are blocked?"` *(Routes strictly to Ops, discarding previous context)*
3. **Ambiguity & Clarification**:
   - `"Show me performance."` *(Expected behavior: clarification question asking which domain, invoking 0 specialists)*
4. **Full Briefing Workflow**:
   - Call `/api/briefing` and verify that Finance, Operations, and Marketing statuses are returned along with the synthesized report.

Run the end-to-end automated test suites locally:
```bash
# Core conversational & routing test suite
py -u scratch/test_conversational_executive.py

# Quality, streaming & briefing reliability evaluation suite
py -u scratch/test_agent_evaluation.py
```

---

## Security & Guardrails

- **Backend-Only Secrets**: API keys are strictly kept server-side. Never expose credentials in React or `VITE_` / `NEXT_PUBLIC_` variables.
- **Tool Execution Security**: Tools execute with the host process permissions; all tool arguments are validated server-side ([Strands Tool Security Guidelines](https://strandsagents.com/docs/user-guide/concepts/tools/)).
- **Safety Limits**: Bounded agent steps (`MAX_AGENT_STEPS = 5`) and token budgets protect against infinite loops.
- **Privacy & Observability**: Internal chain-of-thought is cleanly stripped; log provider metadata, never secrets or raw customer tokens.

---

## Roadmap

### Near Term
- [x] Dedicated conversational Executive Agent (`/api/chat/executive`)
- [x] Multi-turn context resolution and non-repetitive responses
- [x] Zero-specialist clarification and conversational greeting handling
- [x] Dynamic specialist routing with structured findings
- [x] Streaming chat responses (SSE) (`/api/chat/executive/stream`)
- [x] Server-side conversation persistence (`/api/threads`)
- [x] Real-time observability & telemetry telemetry (`/api/observability`)

### Mid Term
- [x] MCP (Model Context Protocol) tool registry (`agents/tools.py`)
- [ ] Live web research tools
- [ ] Enterprise document retrieval (RAG)
- [ ] CRM & SQL database connectors
- [ ] Cost-aware adaptive model routing

### Longer Term
- [ ] Remote A2A (Agent-to-Agent) specialists
- [ ] Persistent organizational memory
- [ ] Role-aware granular access controls
- [ ] Human-in-the-loop approval workflows for consequential business actions

---

## Product Philosophy

AGentic Resolve is not a chatbot that merely rephrases dashboards. Its job is to:

$$\text{Understand} \longrightarrow \text{Route} \longrightarrow \text{Retrieve} \longrightarrow \text{Reason} \longrightarrow \text{Synthesize} \longrightarrow \text{Recommend}$$

Leaders can ask a question, explore a follow-up, pivot direction, and request a decision without manually managing which specialist should work on the problem.
