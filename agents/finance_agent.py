import os
import pandas as pd
import numpy as np

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_SALES_CSV = os.path.join(_DATA_DIR, "sales_sample.csv")


def _load_and_analyze() -> str:
    try:
        df = pd.read_csv(_SALES_CSV)
        df["month"] = pd.to_datetime(df["month"])
        df = df.sort_values(["product", "month"])

        lines = ["=== SALES SUMMARY ==="]
        anomalies = []

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
                    anomalies.append(
                        f"{product} {row['month'].strftime('%Y-%m')}: {atype} "
                        f"${rev:,.0f} vs mean ${mean_r:,.0f} ({dev:+.1f}%)"
                    )

        if anomalies:
            lines.append("Anomalies: " + "; ".join(anomalies))

        return "\n".join(lines)

    except FileNotFoundError:
        return f"ERROR: {_SALES_CSV} not found."
    except Exception as e:
        return f"ERROR computing finance data: {e}"


def run_finance_query(query: str, history: list = None) -> str:
    from groq import Groq
    data_summary = _load_and_analyze()
    client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=5)

    # System message embeds data context once — NOT repeated in every user turn
    messages = [
        {
            "role": "system",
            "content": (
                "You are a financial analyst. Use ONLY the data below to answer questions. "
                "Be concise — 2-3 bullets, under 80 words. Do NOT discuss topics unrelated to finance.\n\n"
                f"[Company Financial Data]\n{data_summary}"
            ),
        }
    ]

    # Replay prior conversation turns (user + assistant messages only)
    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    # Current user question — clean, no data appended
    messages.append({"role": "user", "content": query})

    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


finance_agent = run_finance_query
