## Key Results (2024 Historical Analysis)

| Metric | Value |
|--------|-------|
| Hospitals monitored | 25 |
| CRITICAL risk events detected | 1,781 |
| Hospitals with ≥1 CRITICAL day | 8 of 25 |
| Plants with overdue maintenance | 2 (Barcelona, Zaragoza) |
| ROI on LCS vs. one incident | **13×** |

---

## Project Structure

```
ManOxCo-PI1/
├── infrastructure/
│   └── docker-compose.yml         # Spark cluster + Kafka + MinIO + Jupyter
├── pipelines/
│   ├── run_local.py               # Full pipeline (pandas, no Spark needed)
│   ├── bronze/
│   │   └── ingest_bronze.py       # Raw CSV → Parquet ingestion (Spark)
│   ├── silver/
│   │   └── transform_silver.py    # Cleanse & standardise (Spark)
│   ├── gold/
│   │   └── build_gold.py          # Star schema + risk/financial marts (Spark)
│   └── streaming/
│       ├── simulate_iot_stream.py # Kafka IoT producer (simulates PLC feeds)
│       └── stream_consumer.py     # Spark Structured Streaming consumer
├── app/
│   ├── main.py                    # Streamlit dashboard (7 pages)
│   └── agent/
│       └── decision_agent.py      # AI Decision Copilot (Claude, CLI mode)
├── notebooks/
│   └── ManOxCo_Analysis.ipynb     # Full analytical workbook
├── data/
    ├── data_source/               # Raw CSV inputs (6 datasets)
    ├── bronze/                    # Bronze parquet (auto-generated)
    ├── silver/                    # Silver parquet (auto-generated)
    └── gold/                      # Gold parquet (auto-generated)

```

---

## Architecture

```
IoT PLCs / ERP CSVs
        │
        ▼
  INGESTION LAYER
  Kafka (streaming OT) + Spark Batch (IT)
        │
        ▼
  MEDALLION ARCHITECTURE
  Bronze (raw) → Silver (clean) → Gold (analytics)
        │
        ▼
  AI DECISION COPILOT
  Claude Sonnet + 5 analytical tools
        │
        ▼
  MOMENTUM DASHBOARD
  Streamlit · 7 pages · real-time alerts
```

