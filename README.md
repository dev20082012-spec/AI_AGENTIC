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
> AGentic Resolve is a multi-agent professional assistant that orchestrates specialized AI agents
> in parallel, giving you a unified, decision-ready briefing across Finance, Operations,
> and Marketing in seconds.

</div>

---

## What is AGentic Resolve?

AGentic Resolve acts as the **intelligent command center** for your business.
Powered by the [Strands Agents SDK](https://github.com/strands-agents/sdk-python)
and running on **Amazon Bedrock (Claude Sonnet 5)**, it routes your business query through
an orchestrator that dispatches three specialist sub-agents — all working in **parallel** —
before synthesizing their insights into one crisp, actionable briefing.

Built for the **[Agents for Humans Hackathon](https://agentsforhumans.devpost.com/)** —
Professional Agents track.

---

## Key Features

| Feature | Description |
|---|---|
| Orchestrator Agent | Single entry point — understands your query and delegates intelligently |
| Parallel Execution | All three specialists run and respond before synthesis |
| Finance Agent | Revenue trend analysis, forecasting, historical sales insights |
| Operations Agent | Scheduling automation, email drafting, employee update summaries |
| Marketing Agent | Ad impact analysis, regional and demographic campaign performance |
| Unified Briefing | All specialist outputs synthesized into one decision-ready response |

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full Mermaid flowchart.

```
User Query
  --> Orchestrator Agent (Claude Sonnet 5 / Bedrock)
        |--> finance_specialist   --> Revenue trends, forecasts, anomalies
        |--> ops_specialist       --> Team status, blockers, email drafts
        `--> marketing_specialist --> Campaign analysis, segment rankings
                    |
                    `--> Synthesized Executive Briefing --> User
```

---

## Specialist Agents

### Finance Agent — agents/finance_agent.py

- Revenue trend analysis across product lines (month-over-month)
- Sales forecasting via linear regression on trailing 6 months
- Anomaly detection: flags spikes/drops beyond 2-sigma threshold
- Powered by data/sales_sample.csv

### Operations Agent — agents/ops_agent.py

- Team task status summary grouped by: done / in_progress / pending / blocked
- Flags blocked or stale items (no update in 10+ days) as HIGH PRIORITY
- Professional email draft generator for scheduling requests
- Powered by data/employee_updates.json

### Marketing Agent — agents/marketing_agent.py

- CTR and conversion rate by region and age group, ranked best to worst
- Direct recommendation: which segment to increase investment in, and which to cut
- Powered by data/campaign_sample.csv

---

## Tech Stack

| Technology | Role |
|---|---|
| Python 3.10+ | Core runtime |
| [Strands Agents SDK](https://github.com/strands-agents/sdk-python) | Multi-agent framework (agents-as-tools) |
| Amazon Bedrock | Managed model provider |
| Claude Sonnet 5 | LLM powering all agents |
| pandas / numpy | Data processing inside tool functions |

---

## Project Structure

```
AI_AGENTIC/
|-- agents/
|   |-- finance_agent.py      # Revenue trend analysis and forecasting
|   |-- ops_agent.py          # Scheduling, email drafts, employee updates
|   `-- marketing_agent.py    # Ad impact and market research
|-- data/
|   |-- sales_sample.csv          # Synthetic sales and revenue data
|   |-- employee_updates.json     # Synthetic employee work updates
|   `-- campaign_sample.csv       # Synthetic advertising campaign data
|-- orchestrator.py           # Top-level agent, agents-as-tools pattern
|-- model.py                  # Shared Amazon Bedrock model configuration
|-- requirements.txt          # Python dependencies
|-- ARCHITECTURE.md           # Full Mermaid architecture diagram
|-- README.md
`-- LICENSE                   # MIT
```

> **Note on /data:** All datasets are synthetic sample data standing in for real integrations
> (accounting/sales APIs, calendar APIs, ad-platform APIs). They are designed to produce
> realistic, meaningful analysis outputs during the demo.

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd AI_AGENTIC

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS credentials

You need AWS credentials with Amazon Bedrock access enabled for Claude Sonnet 5
(`us.anthropic.claude-sonnet-4-5-20251001-v1:0`) in region `us-west-2`.

```bash
# Option A: AWS CLI
aws configure

# Option B: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

The model ID and region are defined as constants at the top of model.py and can be
changed in 5 seconds if your Bedrock access is in a different region.

### 4. Run

```bash
python orchestrator.py
```

This fires the sample briefing query through all three specialist agents and prints
a synthesized executive briefing. Delegation routing is printed to the console in
real time so you can see which specialist(s) were called.

---

## License

MIT — see [LICENSE](./LICENSE).

---

<div align="center">

Built with the [Strands Agents SDK](https://github.com/strands-agents/sdk-python) and Amazon Bedrock.

*"One question. Three experts. One answer."*

</div>
