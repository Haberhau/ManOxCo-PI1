"""
Shared data loader for the ManOxCo Streamlit app.
Reads Gold-layer parquet files with caching.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

GOLD = Path(__file__).parent.parent.parent / "data" / "gold"


@st.cache_data(ttl=300)
def load_risk() -> pd.DataFrame:
    df = pd.read_parquet(GOLD / "mart_dryout_risk.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=300)
def load_production() -> pd.DataFrame:
    df = pd.read_parquet(GOLD / "fact_production.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=300)
def load_delivery() -> pd.DataFrame:
    df = pd.read_parquet(GOLD / "fact_delivery.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=300)
def load_consumption() -> pd.DataFrame:
    df = pd.read_parquet(GOLD / "fact_consumption.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=300)
def load_financial() -> pd.DataFrame:
    df = pd.read_parquet(GOLD / "mart_financial.parquet")
    df["date"] = pd.to_datetime(df["year_month"])
    return df


@st.cache_data(ttl=300)
def load_hospitals() -> pd.DataFrame:
    return pd.read_parquet(GOLD / "dim_hospital.parquet")


@st.cache_data(ttl=300)
def load_plants() -> pd.DataFrame:
    return pd.read_parquet(GOLD / "dim_plant.parquet")


def latest_risk_snapshot() -> pd.DataFrame:
    risk = load_risk()
    return (
        risk.sort_values("date")
        .groupby("hospital_name")
        .last()
        .reset_index()
    )


RISK_COLORS = {
    "CRITICAL": "#E84855",
    "HIGH":     "#F4812B",
    "MEDIUM":   "#EAB308",
    "LOW":      "#2EC27E",
}

PLANT_COLORS = {
    "Madrid":    "#4BBFE8",
    "Barcelona": "#0FA3B1",
    "Zaragoza":  "#2EC27E",
    "Alicante":  "#7C3AED",
    "Gijon":     "#F4812B",
}
