# AGentic Resolve — Multi-Agent Architecture

## Overview

AGentic Resolve uses the **agents-as-tools** pattern from the Strands Agents SDK.
The Orchestrator Agent wraps each specialist sub-agent as a callable tool, enabling
intelligent routing and parallel delegation based on the business query.

## Mermaid Flowchart

```mermaid
flowchart TD
    U(["👤 User / Business Analyst"])
    Q["Natural language business query"]
    O["🧠 Orchestrator Agent\nChief-of-Staff\nClaude Sonnet 5 via Amazon Bedrock"]

    U --> Q --> O

    O -->|finance_specialist tool| FA
    O -->|ops_specialist tool| OA
    O -->|marketing_specialist tool| MA

    subgraph SPECIALISTS ["⚡ Parallel Specialist Sub-Agents"]
        FA["💰 Finance Agent\nRevenue · Forecasting · Anomalies"]
        OA["🗓️ Operations Agent\nTeam Status · Scheduling · Email Drafts"]
        MA["📣 Marketing Agent\nCampaign Analysis · Segments · Market Impact"]
    end

    subgraph FINANCE_TOOLS ["Finance Tools"]
        FA --> FT1["load_sales_data()"]
        FA --> FT2["compute_revenue_trend()"]
        FA --> FT3["forecast_next_quarter()"]
        FA --> FT4["detect_anomalies()"]
        FT1 & FT2 & FT3 & FT4 --> FD[("📄 sales_sample.csv")]
    end

    subgraph OPS_TOOLS ["Operations Tools"]
        OA --> OT1["load_employee_updates()"]
        OA --> OT2["summarize_pending_items()"]
        OA --> OT3["draft_scheduling_email()"]
        OT1 & OT2 --> OD[("📄 employee_updates.json")]
    end

    subgraph MARKETING_TOOLS ["Marketing Tools"]
        MA --> MT1["load_campaign_data()"]
        MA --> MT2["analyze_segment_performance()"]
        MA --> MT3["summarize_market_impact()"]
        MT1 & MT2 & MT3 --> MD[("📄 campaign_sample.csv")]
    end

    FA --> SYN["📋 Orchestrator\nSynthesizes all specialist\nresponses into one briefing"]
    OA --> SYN
    MA --> SYN
    SYN --> OUT(["✅ Unified Decision-Ready\nBusiness Briefing"])
    OUT --> U
```

## Component Descriptions

| Component | File | Responsibility |
|---|---|---|
| Orchestrator Agent | `orchestrator.py` | Routes queries, synthesizes responses |
| Finance Agent | `agents/finance_agent.py` | Revenue analysis, forecasting, anomaly detection |
| Operations Agent | `agents/ops_agent.py` | Team status, scheduling, email drafts |
| Marketing Agent | `agents/marketing_agent.py` | Campaign analysis, segment ranking, market impact |
| Shared Model | `model.py` | Single BedrockModel config for all agents |

## Data Flow

1. User submits a natural-language business query to `orchestrator.py`
2. Orchestrator Agent (Claude Sonnet 5) determines which specialist(s) are relevant
3. Relevant specialist agents are called (one, two, or all three in parallel)
4. Each specialist uses its tools to load data, compute metrics, and form an answer
5. Orchestrator synthesizes all specialist responses into a single executive briefing
6. Briefing is returned to the user

## Technology

- **Strands Agents SDK** — Agent framework, agents-as-tools multi-agent pattern
- **Amazon Bedrock** — Managed LLM provider
- **Claude Sonnet 5** (`us.anthropic.claude-sonnet-4-5-20251001-v1:0`) — Model
- **Python 3.10+** / **pandas** / **numpy** — Data processing
