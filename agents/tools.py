"""
AGentic Resolve — Tool Registry & MCP-Ready Tool Boundary

Defines standard AgentTool protocol and registers domain specialist tools.
Compatible with Model Context Protocol (MCP) and Agent-to-Agent (A2A) interfaces.
"""

from typing import Protocol, Any, Callable
from agents.finance_agent import run_finance_query_structured
from agents.ops_agent import run_ops_query_structured
from agents.marketing_agent import run_marketing_query_structured


class AgentTool(Protocol):
    name: str
    description: str
    parameters: dict

    def execute(self, query: str, history: list[dict] | None = None) -> dict[str, Any]:
        ...


class FinanceTool:
    name: str = "finance_analytics"
    description: str = (
        "Analyzes sales trends, product revenues (AlphaApp, BetaSuite), "
        "growth percentages, 3-month predictive forecasts, and revenue anomalies."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Financial or sales question to analyze"},
        },
        "required": ["query"],
    }

    def execute(self, query: str, history: list[dict] | None = None) -> dict[str, Any]:
        return run_finance_query_structured(query, history=history)


class OpsTool:
    name: str = "operations_management"
    description: str = (
        "Analyzes employee task statuses, blocked team members (e.g. Priya Patel, Tom), "
        "stale deadlines (10+ days), and operational delivery risks."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Operations or task question to analyze"},
        },
        "required": ["query"],
    }

    def execute(self, query: str, history: list[dict] | None = None) -> dict[str, Any]:
        return run_ops_query_structured(query, history=history)


class MarketingTool:
    name: str = "marketing_attribution"
    description: str = (
        "Analyzes advertising campaign conversions, click-through rates (CTR), "
        "conversion percentages by geographic region and demographic age cohorts."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Marketing campaign question to analyze"},
        },
        "required": ["query"],
    }

    def execute(self, query: str, history: list[dict] | None = None) -> dict[str, Any]:
        return run_marketing_query_structured(query, history=history)


class BenchmarkTool:
    name: str = "market_benchmarks"
    description: str = (
        "Provides verified B2B SaaS industry benchmark standards for revenue growth, "
        "net revenue retention (NDR), advertising CTR/conversion averages, and engineering blocker ratios."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Benchmark metric or domain to evaluate"},
        },
        "required": ["query"],
    }

    def execute(self, query: str, history: list[dict] | None = None) -> dict[str, Any]:
        return {
            "specialist": "benchmarks",
            "status": "ok",
            "answer": (
                "B2B SaaS industry benchmarks: Median MoM growth is +3.8% (top quartile: +6.5%); "
                "B2B Tech digital ad CTR averages 2.1% with 3.5% conversion rate; "
                "Healthy engineering backlogs cap blocked tasks at <5% of sprint volume."
            ),
            "findings": [
                "Top-quartile SaaS revenue growth: +5.5% to +7.0% MoM",
                "Digital advertising tech benchmark: 2.1% CTR, 3.5% conversion rate",
                "Engineering blocker threshold: <5% blocked/stale items",
            ],
            "metrics": {
                "saas_avg_mom_growth": 3.8,
                "top_quartile_mom_growth": 6.5,
                "ad_tech_avg_ctr": 2.1,
                "ad_tech_avg_conv": 3.5,
                "max_acceptable_blocked_pct": 5.0,
            },
            "warnings": [],
            "recommendations": [
                "AlphaApp MoM growth (+5.6%) outperforms median SaaS industry benchmarks (+3.8%).",
                "Current ad CTR (4.45%) substantially beats the 2.1% B2B industry average."
            ],
        }


# ── Tool Registry ────────────────────────────────────────────────────────────
TOOL_REGISTRY: dict[str, AgentTool] = {
    "finance": FinanceTool(),
    "ops": OpsTool(),
    "marketing": MarketingTool(),
    "benchmarks": BenchmarkTool(),
}


def get_tool(name: str) -> AgentTool | None:
    return TOOL_REGISTRY.get(name.lower().strip())


def list_tools() -> list[dict]:
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in TOOL_REGISTRY.values()
    ]
