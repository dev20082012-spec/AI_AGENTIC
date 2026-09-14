import os
import pandas as pd
from model import chat_completion

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_CAMPAIGN_CSV = os.path.join(_DATA_DIR, "campaign_sample.csv")


def get_marketing_data() -> dict:
    """Computes exact, deterministic campaign analytics from campaign_sample.csv."""
    try:
        df = pd.read_csv(_CAMPAIGN_CSV)

        total_imp = int(df["impressions"].sum())
        total_clicks = int(df["clicks"].sum())
        total_conv = int(df["conversions"].sum())
        avg_ctr = round((total_clicks / total_imp) * 100, 2) if total_imp > 0 else 0
        avg_conv = round((total_conv / total_clicks) * 100, 2) if total_clicks > 0 else 0

        def rank_col(col):
            agg = df.groupby(col).agg(
                clicks=("clicks", "sum"),
                conversions=("conversions", "sum"),
            ).reset_index()
            agg["conv_pct"] = (agg["conversions"] / agg["clicks"] * 100).round(2)
            return agg.sort_values("conv_pct", ascending=False)

        reg = rank_col("region")
        age = rank_col("age_group")

        best_r, worst_r = reg.iloc[0], reg.iloc[-1]
        best_a, worst_a = age.iloc[0], age.iloc[-1]

        lines = [
            f"Campaign Totals: Conversions={total_conv:,}, Avg CTR={avg_ctr}%, Avg Conv={avg_conv}%",
            f"Top Segments: Region='{best_r['region']}' ({best_r['conv_pct']}% conv, {int(best_r['conversions']):,} conv) | Age='{best_a['age_group']}' ({best_a['conv_pct']}% conv)",
            f"Lowest Segments: Region='{worst_r['region']}' ({worst_r['conv_pct']}% conv) | Age='{worst_a['age_group']}' ({worst_a['conv_pct']}% conv)",
        ]

        return {
            "totals": {
                "impressions": total_imp,
                "clicks": total_clicks,
                "conversions": total_conv,
                "avg_ctr": avg_ctr,
                "avg_conv": avg_conv,
            },
            "top_region": {"region": best_r["region"], "conv_pct": best_r["conv_pct"]},
            "worst_region": {"region": worst_r["region"], "conv_pct": worst_r["conv_pct"]},
            "top_age": {"age_group": best_a["age_group"], "conv_pct": best_a["conv_pct"]},
            "worst_age": {"age_group": worst_a["age_group"], "conv_pct": worst_a["conv_pct"]},
            "summary_text": "\n".join(lines),
            "status": "ok",
        }

    except FileNotFoundError:
        return {"status": "error", "error": f"{_CAMPAIGN_CSV} not found.", "summary_text": "Marketing data unavailable."}
    except Exception as e:
        return {"status": "error", "error": str(e), "summary_text": f"Error computing campaign data: {e}"}


def _load_and_analyze() -> str:
    data = get_marketing_data()
    return data.get("summary_text", "")


def run_marketing_query_structured(query: str, history: list = None) -> dict:
    """Executes a marketing query returning structured findings, segment ROI, and conversational answer."""
    data = get_marketing_data()
    data_summary = data.get("summary_text", "")

    messages = [
        {
            "role": "system",
            "content": (
                "You are the Marketing Specialist for an executive business intelligence system. "
                "Use ONLY the campaign data below to answer questions. "
                "Focus on CTR, conversion rate, ad attribution, and demographic/regional segments. "
                "Be direct, actionable, and analytical.\n\n"
                f"[Campaign Data]\n{data_summary}"
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

    return {
        "specialist": "marketing",
        "answer": answer,
        "metrics": data.get("totals", {}),
        "segments": {
            "top_region": data.get("top_region"),
            "top_age": data.get("top_age"),
        },
        "warnings": [],
    }


def run_marketing_query(query: str, history: list = None) -> str:
    """Maintains backward compatibility returning pure text answer."""
    res = run_marketing_query_structured(query, history=history)
    return res["answer"]


def load_campaign_data():
    return pd.read_csv(_CAMPAIGN_CSV)


def analyze_segment_performance():
    return _load_and_analyze()


def summarize_market_impact():
    return _load_and_analyze()


marketing_agent = run_marketing_query
