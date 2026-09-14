<div align="center">

# 🤖 AGentic Resolve

### *Your AI-Powered Chief of Staff*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Claude_Sonnet_5-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Strands SDK](https://img.shields.io/badge/Strands_Agents_SDK-Multi--Agent-6C3483?style=for-the-badge)](https://github.com/strands-agents/sdk-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](./LICENSE)
[![Hackathon](https://img.shields.io/badge/Hackathon-Agents_for_Humans-EC4899?style=for-the-badge)](https://agentsforhumans.devpost.com/)

<br/>

> **Ask one question. Get three expert answers. Instantly.**
>
> AGentic Resolve is a multi-agent professional assistant that orchestrates specialized AI agents in parallel —
> giving you a unified, decision-ready briefing across Finance, Operations, and Marketing in seconds.

</div>

---

## 🎯 What is AGentic Resolve?

AGentic Resolve acts as the **intelligent command center** for your business. Powered by the [Strands Agents SDK](https://github.com/strands-agents/sdk-python) and running on **Amazon Bedrock (Claude Sonnet 5)**, it routes your business query through an orchestrator that dispatches three specialist sub-agents — all working in **parallel** — before synthesizing their insights into one crisp, actionable briefing.

Built for the **[Agents for Humans Hackathon](https://agentsforhumans.devpost.com/)** — Professional Agents track. 🏆

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Orchestrator Agent** | Single entry point — understands your query and delegates intelligently |
| ⚡ **Parallel Execution** | All three specialists run simultaneously — no waiting in line |
| 💰 **Finance Agent** | Revenue trend analysis, forecasting, historical sales insights |
| 🗓️ **Operations Agent** | Scheduling automation, email drafting, employee update summaries |
| 📣 **Marketing Agent** | Ad impact analysis, regional & demographic campaign performance |
| 📋 **Unified Briefing** | All specialist outputs synthesized into one decision-ready response |

---

## 🏗️ Architecture

### System Flowchart

```mermaid
flowchart TD
    U(["👤 User / Business Analyst"]):::user
    O["🧠 Orchestrator Agent\nClaude Sonnet 5 via Bedrock"]:::orchestrator

    U -->|"Natural language query"| O

    O -->|"Delegates via agents-as-tools"| F
    O -->|"Delegates via agents-as-tools"| Ops
    O -->|"Delegates via agents-as-tools"| M

    subgraph PARALLEL ["⚡ Parallel Specialist Agents"]
        direction TB
        F["💰 Finance Agent\nfinance_specialist tool"]:::finance
        Ops["🗓️ Operations Agent\nops_specialist tool"]:::ops
        M["📣 Marketing Agent\nmarketing_specialist tool"]:::marketing
    end

    subgraph TOOLS_F ["Finance Tools"]
        F --> F1["📈 Revenue Trend Analysis"]
        F --> F2["🔮 Sales Forecasting"]
        F --> F3["🗂️ Historical Data - sales_sample.csv"]
    end

    subgraph TOOLS_O ["Operations Tools"]
        Ops --> O1["📅 Schedule Automation"]
        Ops --> O2["✉️ Email Draft Generator"]
        Ops --> O3["📝 Employee Updates - employee_updates.json"]
    end

    subgraph TOOLS_M ["Marketing Tools"]
        M --> M1["🌍 Regional Campaign Analysis"]
        M --> M2["👥 Demographic Targeting Insights"]
        M --> M3["📊 Ad Impact Data - campaign_sample.csv"]
    end

    F --> R["📋 Orchestrator Synthesizes All Results"]
    Ops --> R
    M --> R
    R --> U2(["✅ Unified Decision-Ready Briefing"]):::output

    classDef user fill:#4F46E5,color:#fff,stroke:#3730A3
    classDef orchestrator fill:#7C3AED,color:#fff,stroke:#5B21B6
    classDef finance fill:#059669,color:#fff,stroke:#047857
    classDef ops fill:#D97706,color:#fff,stroke:#B45309
    classDef marketing fill:#DB2777,color:#fff,stroke:#BE185D
    classDef output fill:#0EA5E9,color:#fff,stroke:#0284C7
```

### Flow Summary

```
👤 User Query
    └─▶ 🧠 Orchestrator Agent
            ├─▶ 💰 finance_specialist   ──▶ Sales data + forecasting
            ├─▶ 🗓️ ops_specialist       ──▶ Schedules + email drafts + updates
            └─▶ 📣 marketing_specialist ──▶ Campaign + regional + demographic data
                        │
                        └─▶ 📋 Synthesized Briefing ──▶ ✅ Decision-Ready Output
```

> 📄 For the complete technical diagram, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 🤖 The Specialist Agents

### 💰 Finance Agent — `agents/finance_agent.py`

Crunches your numbers and looks ahead:
- 📈 Revenue trend analysis across product lines
- 🔮 Sales forecasting based on historical patterns
- 📊 Market activity monitoring
- 🗂️ Powered by `data/sales_sample.csv`

### 🗓️ Operations Agent — `agents/ops_agent.py`

Handles the operational backbone of your business:
- 📅 Automated scheduling and calendar management
- ✉️ Professional email drafting
- 📝 Summarizing employee work updates and blockers
- 🗂️ Powered by `data/employee_updates.json`

### 📣 Marketing Agent — `agents/marketing_agent.py`

Decodes what's actually driving growth:
- 🌍 Regional campaign performance breakdown
- 👥 Age group and demographic targeting analysis
- 💡 Ad impact attribution — which campaigns are moving the needle
- 🗂️ Powered by `data/campaign_sample.csv`

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| 🐍 **Python 3.10+** | Core runtime |
| 🤖 **[Strands Agents SDK](https://github.com/strands-agents/sdk-python)** | Multi-agent framework (agents-as-tools pattern) |
| ☁️ **Amazon Bedrock** | Managed model provider |
| 🧠 **Claude Sonnet 5** | LLM powering all agents |

---

## 📦 Project Structure

```
AI_AGENTIC/
├── 🤖 agents/
│   ├── finance_agent.py      # 💰 Revenue trend analysis + forecasting
│   ├── ops_agent.py          # 🗓️ Scheduling, email drafts, employee updates
│   └── marketing_agent.py    # 📣 Ad impact + market research
│
├── 📊 data/
│   ├── sales_sample.csv          # 💰 Synthetic sales & revenue data
│   ├── employee_updates.json     # 🗓️ Synthetic employee work updates
│   └── campaign_sample.csv       # 📣 Synthetic advertising campaign data
│
├── 🧠 orchestrator.py        # Top-level agent, agents-as-tools pattern
├── ⚙️  model.py               # Shared Amazon Bedrock model configuration
├── 📋 requirements.txt       # Python dependencies
├── 🏗️  ARCHITECTURE.md        # Full architecture diagram
├── 📖 README.md
└── 📄 LICENSE                # MIT
```

---

## 🚀 Getting Started

### 1️⃣ Clone & Set Up Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd AI_AGENTIC

# Create and activate a virtual environment
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure AWS Credentials

Make sure your AWS credentials have **Amazon Bedrock** access enabled for **Claude Sonnet 5**.

```bash
# Option A: AWS CLI
aws configure

# Option B: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

> ⚠️ **Note:** The default region is `us-west-2`. If your Bedrock access is in a different region,
> update the region and model ID in `model.py`.

### 4️⃣ Run the Orchestrator

```bash
python orchestrator.py
```

This fires a sample business query through the orchestrator and prints the **combined expert briefing** from all three specialist agents. 🎉

---

## 📊 Sample Data

All datasets in `/data` are **fully synthetic** — generated specifically to demonstrate the agents' reasoning and delegation logic end-to-end with realistic patterns. No real business data is included.

| File | Agent | Contents |
|---|---|---|
| `sales_sample.csv` | 💰 Finance | Historical revenue, product performance, time-series trends |
| `employee_updates.json` | 🗓️ Operations | Team updates, blockers, task statuses |
| `campaign_sample.csv` | 📣 Marketing | Ad spend, impressions, conversions by region & demographic |

---

## 🏆 Hackathon

AGentic Resolve was built for the **[Agents for Humans Hackathon](https://agentsforhumans.devpost.com/)** — **Professional Agents** track.

The core design challenge: *How do you make a single AI agent feel like an entire expert team?*
The answer: **orchestrate multiple specialist agents and synthesize their outputs intelligently.**

---

## 🔭 What's Next

The roadmap for AGentic Resolve beyond the hackathon:

- 🔗 **Real API integrations** — accounting/sales APIs (QuickBooks, Salesforce), calendar/email (Google Workspace, Microsoft 365), and ad-platform APIs (Google Ads, Meta)
- ☁️ **Amazon Bedrock AgentCore** deployment for production-scale orchestration
- 📊 **Visual Dashboard** — a real-time UI for the orchestrator's briefings
- 🔔 **Proactive Alerts** — agents that surface critical insights without being asked
- 🔐 **Role-based access** — different briefing depths for different stakeholders

---

## 📄 License

MIT — see [LICENSE](./LICENSE) for full details.

---

<div align="center">

Built with ❤️ and ☕ using the [Strands Agents SDK](https://github.com/strands-agents/sdk-python) and Amazon Bedrock.

*"One question. Three experts. One answer."*

</div>
