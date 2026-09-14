import os
import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_CAMPAIGN_CSV = os.path.join(_DATA_DIR, "campaign_sample.csv")


def _load_and_analyze() -> str:
    try:
        df = pd.read_csv(_CAMPAIGN_CSV)

        def rank_by(col):
            agg = df.groupby(col).agg(
                impressions=("impressions", "sum"),
                clicks=("clicks", "sum"),
                conversions=("conversions", "sum"),
            ).reset_index()
            agg["ctr_pct"] = (agg["clicks"] / agg["impressions"] * 100).round(2)
            agg["conv_pct"] = (agg["conversions"] / agg["clicks"] * 100).round(2)
            return agg.sort_values("conv_pct", ascending=False)

        regions = rank_by("region")
        age_groups = rank_by("age_group")

        lines = ["=== CAMPAIGN PERFORMANCE SUMMARY ==="]

        lines.append("\nBy Region (ranked by conversion rate):")
        for _, row in regions.iterrows():
            lines.append(
                f"  {row['region']}: conv={row['conv_pct']}%, CTR={row['ctr_pct']}%, "
                f"conversions={int(row['conversions']):,}"
            )

        lines.append("\nBy Age Group (ranked by conversion rate):")
        for _, row in age_groups.iterrows():
            lines.append(
                f"  {row['age_group']}: conv={row['conv_pct']}%, CTR={row['ctr_pct']}%, "
                f"conversions={int(row['conversions']):,}"
            )

        best_r = regions.iloc[0]
        worst_r = regions.iloc[-1]
        best_a = age_groups.iloc[0]
        worst_a = age_groups.iloc[-1]

        lines.append(
            f"\nTOP: Region='{best_r['region']}' ({best_r['conv_pct']}% conv) | "
            f"Age='{best_a['age_group']}' ({best_a['conv_pct']}% conv)"
        )
        lines.append(
            f"WORST: Region='{worst_r['region']}' ({worst_r['conv_pct']}% conv) | "
            f"Age='{worst_a['age_group']}' ({worst_a['conv_pct']}% conv)"
        )

        return "\n".join(lines)

    except FileNotFoundError:
        return f"ERROR: {_CAMPAIGN_CSV} not found."
    except Exception as e:
        return f"ERROR computing campaign data: {e}"


def run_marketing_query(query: str) -> str:
    from groq import Groq
    data_summary = _load_and_analyze()
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a market research analyst. Answer the query using the campaign data. "
                    "Give a direct recommendation with specific numbers. Max 3 bullet points. Be brief."
                ),
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\n{data_summary}",
            },
        ],
        max_tokens=400,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
