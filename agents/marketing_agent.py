import os
import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_CAMPAIGN_CSV = os.path.join(_DATA_DIR, "campaign_sample.csv")


def _load_and_analyze() -> str:
    try:
        df = pd.read_csv(_CAMPAIGN_CSV)

        total_imp = df["impressions"].sum()
        total_clicks = df["clicks"].sum()
        total_conv = df["conversions"].sum()
        avg_ctr = round((total_clicks / total_imp) * 100, 2)
        avg_conv = round((total_conv / total_clicks) * 100, 2)

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
        return "\n".join(lines)

    except FileNotFoundError:
        return f"ERROR: {_CAMPAIGN_CSV} not found."
    except Exception as e:
        return f"ERROR computing campaign data: {e}"


def run_marketing_query(query: str, history: list = None) -> str:
    from groq import Groq
    data_summary = _load_and_analyze()
    client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=5)

    # Data context embedded in system message once — not repeated every user turn
    messages = [
        {
            "role": "system",
            "content": (
                "You are a marketing analyst. Use ONLY the data below to answer questions. "
                "Be concise — 2-3 bullets, under 80 words. Focus on conversion, CTR, and segment performance.\n\n"
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

    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def load_campaign_data():
    return pd.read_csv(_CAMPAIGN_CSV)


def analyze_segment_performance():
    return _load_and_analyze()


def summarize_market_impact():
    return _load_and_analyze()


marketing_agent = run_marketing_query
