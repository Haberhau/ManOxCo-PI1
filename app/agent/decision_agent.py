"""
ManOxCo Oxygen Reliability Decision Copilot - PI-1
AI agent powered by Claude that queries Gold-layer analytical tables
and provides executive-level recommendations on:
  - Dry-out risk alerts
  - Maintenance scheduling
  - Logistics optimisation
  - Financial exposure
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(Path(__file__).parents[2] / ".env")

GOLD_PATH = Path(os.environ.get("GOLD_PATH", str(Path(__file__).parents[2] / "data" / "gold")))

client = Anthropic()

SYSTEM_PROMPT = """You are the LCS Copilot — the AI decision intelligence layer of
Momentum's Liquid Control System, deployed for ManOxCo.

Momentum's mission: From Signal to Safety.
Your mission: close the gap between operational data and the decisions that prevent crises.

You have access to analytical tools that query the ManOxCo Gold-layer platform:
- get_dryout_risk_summary: hospital fill levels, risk scores, and days-to-dryout
- get_production_summary: plant output and storage across the network
- get_financial_summary: revenue, cost, and margin exposure by plant and month
- get_maintenance_schedule: plant shutdown history and optimal upcoming windows
- get_critical_alerts: hospitals currently below minimum refill threshold

How you operate:
1. Always check critical alerts first — patient safety is the top priority
2. Reason across domains simultaneously (production + logistics + consumption + finance)
3. Give precise numbers, not vague summaries
4. Grade every finding: [URGENT], [HIGH], [MEDIUM], [LOW]
5. End every response with a concrete recommended action, not just analysis
6. Speak as a senior operations director with AI-level data access

You are not a chatbot. You are a decision engine.
The January 2025 incident happened because no one had a system like you.
That does not happen again.
"""

# ── Tool implementations ──────────────────────────────────────────────────────

def _load_parquet(name: str) -> pd.DataFrame:
    path = GOLD_PATH / f"{name}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def get_dryout_risk_summary(days_ahead: int = 7) -> dict:
    df = _load_parquet("mart_dryout_risk")
    if df.empty:
        return {"error": "No risk data available. Run the Gold pipeline first."}

    df["date"] = pd.to_datetime(df["date"])
    cutoff = pd.Timestamp.now().normalize() + timedelta(days=days_ahead)
    recent = df[df["date"] >= pd.Timestamp.now().normalize() - timedelta(days=3)]

    summary = (
        recent
        .groupby(["hospital_city", "hospital_name"])
        .agg(
            latest_fill_pct=("fill_pct", "last"),
            min_fill_pct=("fill_pct", "min"),
            risk_level=("risk_level", "last"),
            days_to_dryout=("days_to_dryout", "last"),
            avg_daily_consumption=("daily_consumption_tons", "mean"),
        )
        .reset_index()
        .sort_values("latest_fill_pct")
    )

    return {
        "as_of": str(date.today()),
        "hospitals_at_critical_risk": summary[summary["risk_level"] == "CRITICAL"].to_dict("records"),
        "hospitals_at_high_risk": summary[summary["risk_level"] == "HIGH"].to_dict("records"),
        "full_summary": summary.head(10).to_dict("records"),
    }


def get_production_summary() -> dict:
    prod = _load_parquet("fact_production")
    if prod.empty:
        return {"error": "No production data available."}

    prod["date"] = pd.to_datetime(prod["date"])
    last_30 = prod[prod["date"] >= (pd.Timestamp.now() - timedelta(days=30))]

    summary = (
        last_30
        .groupby("plant")
        .agg(
            avg_daily_production=("production_tons", "mean"),
            total_production=("production_tons", "sum"),
            latest_stored=("stored_tons", "last"),
            avg_utilisation=("utilisation_pct", "mean"),
        )
        .reset_index()
    )
    return {
        "period": "last_30_days",
        "plant_summary": summary.to_dict("records"),
    }


def get_financial_summary(months: int = 3) -> dict:
    fin = _load_parquet("mart_financial")
    if fin.empty:
        return {"error": "No financial data available."}

    recent = fin.sort_values("year_month").tail(months * 5)
    total = recent.groupby("year_month").agg(
        total_revenue=("total_revenue", "sum"),
        total_cost=("total_cost", "sum"),
        gross_margin=("gross_margin", "sum"),
    ).reset_index()
    total["margin_pct"] = total["gross_margin"] / total["total_revenue"].replace(0, 1)

    by_plant = recent.groupby("plant").agg(
        avg_margin_pct=("margin_pct", "mean"),
        total_revenue=("total_revenue", "sum"),
        total_cost=("total_cost", "sum"),
    ).reset_index()

    return {
        "monthly_totals": total.to_dict("records"),
        "by_plant": by_plant.to_dict("records"),
    }


def get_maintenance_schedule() -> dict:
    last_shutdowns = {
        "Madrid":    {"last_shutdown": "2025-01-01", "duration_days": 22, "recommended_interval_years": 2},
        "Barcelona": {"last_shutdown": "2023-08-01", "duration_days": 20, "recommended_interval_years": 2},
        "Zaragoza":  {"last_shutdown": "2023-06-01", "duration_days": 15, "recommended_interval_years": 3},
        "Alicante":  {"last_shutdown": "2023-12-01", "duration_days": 12, "recommended_interval_years": 3},
        "Gijon":     {"last_shutdown": "2023-10-01", "duration_days": 8,  "recommended_interval_years": 3},
    }

    today = date.today()
    schedule = []
    for plant, info in last_shutdowns.items():
        last = date.fromisoformat(info["last_shutdown"])
        next_due = last.replace(year=last.year + info["recommended_interval_years"])
        days_until = (next_due - today).days
        schedule.append({
            "plant": plant,
            "last_shutdown": info["last_shutdown"],
            "duration_days": info["duration_days"],
            "next_recommended": str(next_due),
            "days_until_due": days_until,
            "status": "OVERDUE" if days_until < 0 else ("DUE_SOON" if days_until < 90 else "OK"),
        })

    return {"maintenance_schedule": sorted(schedule, key=lambda x: x["days_until_due"])}


def get_critical_alerts() -> dict:
    risk = _load_parquet("mart_dryout_risk")
    if risk.empty:
        return {"alerts": [], "note": "No data available"}

    risk["date"] = pd.to_datetime(risk["date"])
    latest = risk.sort_values("date").groupby("hospital_name").last().reset_index()
    critical = latest[latest["risk_level"] == "CRITICAL"]

    alerts = []
    for _, row in critical.iterrows():
        alerts.append({
            "severity": "CRITICAL",
            "hospital": row["hospital_name"],
            "city": row["hospital_city"],
            "fill_pct": round(row["fill_pct"] * 100, 1),
            "days_to_dryout": round(row["days_to_dryout"], 1),
            "action": f"Dispatch truck to {row['hospital_name']} immediately",
        })

    return {
        "alert_count": len(alerts),
        "alerts": alerts,
        "as_of": str(date.today()),
    }


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_dryout_risk_summary",
        "description": "Returns hospital LOX dry-out risk scores, fill levels, and days-to-dryout. Sorted from most critical to safest.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "How many days ahead to consider for risk window",
                    "default": 7,
                }
            },
        },
    },
    {
        "name": "get_production_summary",
        "description": "Returns LOX production volumes, storage levels, and plant utilisation for the last 30 days.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_financial_summary",
        "description": "Returns revenue, cost, and margin by plant and month.",
        "input_schema": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of recent months to summarise",
                    "default": 3,
                }
            },
        },
    },
    {
        "name": "get_maintenance_schedule",
        "description": "Returns recommended maintenance windows for each plant based on last shutdown dates and recommended intervals.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_critical_alerts",
        "description": "Returns hospitals currently below their minimum refill threshold — immediate action required.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

TOOL_FN_MAP = {
    "get_dryout_risk_summary": get_dryout_risk_summary,
    "get_production_summary": get_production_summary,
    "get_financial_summary": get_financial_summary,
    "get_maintenance_schedule": get_maintenance_schedule,
    "get_critical_alerts": get_critical_alerts,
}


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(user_query: str) -> str:
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(text_blocks)

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    fn = TOOL_FN_MAP.get(block.name)
                    result = fn(**block.input) if fn else {"error": f"Unknown tool: {block.name}"}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return "Agent could not produce a response."


# ── CLI ───────────────────────────────────────────────────────────────────────

STARTER_QUERIES = [
    "Give me an executive briefing on current dry-out risk across all hospitals.",
    "Which plants need maintenance soon and how should we sequence them to avoid supply gaps?",
    "What is our financial exposure this quarter and which plants are underperforming?",
    "Are there any critical alerts right now that require immediate action?",
]

if __name__ == "__main__":
    print("=" * 70)
    print("LUMINAE INTELLIGENCE — LCS Copilot")
    print("Liquid Control System | ManOxCo Oxygen Reliability Platform")
    print("From Signal to Safety.")
    print("=" * 70)
    print("\nStarter queries:")
    for i, q in enumerate(STARTER_QUERIES, 1):
        print(f"  {i}. {q}")
    print()

    while True:
        query = input("Ask the Copilot (or 'quit'): ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if query.isdigit() and 1 <= int(query) <= len(STARTER_QUERIES):
            query = STARTER_QUERIES[int(query) - 1]
            print(f"Query: {query}\n")

        print("\n" + "─" * 70)
        answer = run_agent(query)
        print(answer)
        print("─" * 70 + "\n")
