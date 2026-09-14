import os
import pandas as pd
import numpy as np
from model import chat_completion

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_SALES_CSV = os.path.join(_DATA_DIR, "sales_sample.csv")


def get_finance_data() -> dict:
    """Computes exact, deterministic financial analytics from sales_sample.csv."""
    try:
        df = pd.read_csv(_SALES_CSV)
        df["month"] = pd.to_datetime(df["month"])
        df = df.sort_values(["product", "month"])

        lines = ["=== SALES SUMMARY ==="]
        anomalies = []
        products_data = {}

        for product, grp in df.groupby("product"):
            grp = grp.copy().reset_index(drop=True)
            revenues = grp["revenue"].values.astype(float)
            first, last = revenues[0], revenues[-1]
            total_growth = round(((last - first) / first) * 100, 1)
            avg_mom = round(float(pd.Series(revenues).pct_change().mean() * 100), 1)

            tail_rev = revenues[-6:]
            x = list(range(len(tail_rev)))
            m, b = np.polyfit(x, tail_rev, 1)
            next_q = [round(max(m * (5 + i) + b, 0), 0) for i in range(1, 4)]

            products_data[product] = {
                "start_revenue": first,
                "latest_revenue": last,
                "growth_pct": total_growth,
                "avg_mom_pct": avg_mom,
                "forecast_3m": next_q,
            }

            lines.append(
                f"{product}: ${first:,.0f} -> ${last:,.0f} "
                f"(+{total_growth}%, avg MoM: +{avg_mom}%). "
                f"3M Forecast: ${next_q[0]:,.0f} / ${next_q[1]:,.0f} / ${next_q[2]:,.0f}"
            )

            mean_r, std_r = revenues.mean(), revenues.std()
            for _, row in grp.iterrows():
                rev = float(row["revenue"])
                if abs(rev - mean_r) > 1.5 * std_r:
                    dev = round(((rev - mean_r) / mean_r) * 100, 1)
                    atype = "SPIKE" if rev > mean_r else "DROP"
                    anomaly_str = (
                        f"{product} {row['month'].strftime('%Y-%m')}: {atype} "
                        f"${rev:,.0f} vs mean ${mean_r:,.0f} ({dev:+.1f}%)"
                    )
                    anomalies.append(anomaly_str)

        if anomalies:
            lines.append("Anomalies: " + "; ".join(anomalies))

        return {
            "products": products_data,
            "anomalies": anomalies,
            "summary_text": "\n".join(lines),
            "status": "ok",
        }

    except FileNotFoundError:
        return {"status": "error", "error": f"{_SALES_CSV} not found.", "summary_text": "Financial data unavailable."}
    except Exception as e:
        return {"status": "error", "error": str(e), "summary_text": f"Error computing financial data: {e}"}


def _load_and_analyze() -> str:
    data = get_finance_data()
    return data.get("summary_text", "")


def run_finance_query_structured(query: str, history: list = None) -> dict:
    """Executes a financial query returning structured findings, metrics, and conversational answer."""
    data = get_finance_data()
    data_summary = data.get("summary_text", "")

    messages = [
        {
            "role": "system",
            "content": (
                "You are the Finance Specialist for an executive business intelligence system. "
                "Use ONLY the company financial data below to answer questions. "
                "Be direct, insightful, and concise. Highlight key revenue drivers, trends, forecasts, and anomalies. "
                "Do NOT invent numbers outside this dataset.\n\n"
                f"[Company Financial Data]\n{data_summary}"
            ),
        }
    ]

    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": query})

    answer = chat_completion(messages, max_tokens=280, temperature=0.3)

    findings = []
    for prod, pdata in data.get("products", {}).items():
        findings.append(f"{prod}: Revenue ${pdata.get('latest_revenue',0):,.0f} (+{pdata.get('growth_pct',0)}% growth)")
    
    recommendations = [
        "Sustain growth momentum in leading product AlphaApp while auditing BetaSuite acquisition costs.",
        "Monitor anomaly periods for seasonal variations vs operational issues."
    ]

    return {
        "specialist": "finance",
        "answer": answer,
        "findings": findings,
        "metrics": data.get("products", {}),
        "anomalies": data.get("anomalies", []),
        "warnings": data.get("anomalies", [])[:2],
        "recommendations": recommendations,
    }


def run_finance_query(query: str, history: list = None) -> str:
    """Maintains backward compatibility returning pure text answer."""
    res = run_finance_query_structured(query, history=history)
    return res["answer"]


finance_agent = run_finance_query
