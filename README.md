# AGentic Resolve

A multi-agent professional assistant built with the [Strands Agents SDK](https://github.com/strands-agents/sdk-python), 
running on Amazon Bedrock (Claude Sonnet 5). Built for the **Agents for Humans Hackathon** (Professional Agents track).

## What it does

AGentic Resolve is a "chief of staff" for a business. Ask it one question, and an 
**orchestrator agent** delegates to three specialist sub-agents running in parallel:

- **Finance Agent** — revenue trend analysis and forecasting on existing products, based on 
  historical sales data and current market activity.
- **Operations Agent** — automates scheduling, email drafting, and summarizing employee 
  work updates.
- **Marketing Agent** — analyzes advertising impact: which regions, age groups, and 
  campaigns are driving real market traction.

The orchestrator synthesizes all three specialist responses into one decision-ready briefing.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full diagram.

User query → Orchestrator Agent → routes to one or more of:
`finance_specialist` / `ops_specialist` / `marketing_specialist` tools → 
each backed by its own Strands `Agent` with dedicated tools and sample data → 
synthesized response back to the user.

## Tech stack

- [Strands Agents SDK](https://github.com/strands-agents/sdk-python) — agent framework, 
  agents-as-tools multi-agent pattern
- Amazon Bedrock — model provider (Claude Sonnet 5)
- Python 3.10+

## Setup

\`\`\`bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
\`\`\`

Configure AWS credentials with Bedrock access enabled for Claude Sonnet 5 in your target region 
(default: `us-west-2`). Update the region/model ID in `model.py` if your access is in a 
different region.

## Run

\`\`\`bash
python orchestrator.py
\`\`\`

This runs a sample business query through the orchestrator and prints the combined briefing 
from all three specialist agents.

## Project structure

\`\`\`
AI_AGENTIC/
├── agents/
│   ├── finance_agent.py     # revenue trend + forecasting
│   ├── ops_agent.py         # scheduling, email drafts, employee updates
│   └── marketing_agent.py   # ad impact / market research
├── data/
│   ├── sales_sample.csv
│   ├── employee_updates.json
│   └── campaign_sample.csv
├── orchestrator.py          # top-level agent, agents-as-tools pattern
├── model.py                 # shared Bedrock model config
├── requirements.txt
├── ARCHITECTURE.md
└── LICENSE
\`\`\`

## Data

All datasets in `/data` are synthetic sample data generated to demonstrate the agents' 
reasoning and delegation logic end-to-end. See "What's next" below for planned real 
integrations.

## Hackathon

Built for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com/) — 
Professional Agents track.

## What's next

Replacing sample datasets with real integrations (accounting/sales APIs, calendar/email APIs, 
ad-platform APIs), deployment on Amazon Bedrock AgentCore, and a visual dashboard for the 
orchestrator's briefings.

## License

MIT — see [LICENSE](./LICENSE).
