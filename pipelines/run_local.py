import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date, timedelta
import warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
SRC  = ROOT / "data" / "data_source"
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD   = ROOT / "data" / "gold"

for p in [BRONZE, SILVER, GOLD]:
    p.mkdir(parents=True, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def eu_float(s):
    """Parse European-format numbers: '1.234,56' → 1234.56"""
    if pd.isna(s):
        return np.nan
    s = str(s).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


def read_tsv(name, encoding="ISO-8859-1", **kwargs):
    return pd.read_csv(SRC / name, sep="\t", encoding=encoding, dtype=str, **kwargs)


# ══ BRONZE ════════════════════════════════════════════════════════════════════

print("── BRONZE ──────────────────────────────────────────────────────────────")

# Plants production
df = read_tsv("plants_production_export.csv",
              names=["date","plant","production_tons","stored_tons","delivered_tons"],
              header=0)
df["_source"] = "plants_production_export"
df.to_parquet(BRONZE / "plants_production.parquet", index=False)
print(f"  plants_production: {len(df):,} rows")

# Plants data
df = read_tsv("plants_data.csv",
              names=["plant","max_daily_prod","max_storage","prod_eff","storage_eff",
                     "cost_energy","other_cost","fixed_monthly_cost"],
              header=0)
df["_source"] = "plants_data"
df.to_parquet(BRONZE / "plants_data.parquet", index=False)
print(f"  plants_data: {len(df):,} rows")

# LOX delivery
df = read_tsv("lox_delivery_export.csv",
              names=["date","truck","hospital_city","hospital_name","refill_tons",
                     "delivery_cost","product_price","total_bill","over_delivery"],
              header=0)
df["_source"] = "lox_delivery_export"
df.to_parquet(BRONZE / "lox_delivery.parquet", index=False)
print(f"  lox_delivery: {len(df):,} rows")

# Hospital data
df = read_tsv("lox_hosp_data.csv",
              names=["hospital_city","hospital_name","storage_capacity_tons",
                     "min_refill_pct","price_per_ton"],
              header=0)
df["_source"] = "lox_hosp_data"
df.to_parquet(BRONZE / "hospital_data.parquet", index=False)
print(f"  hospital_data: {len(df):,} rows")

# Hospital consumption
df = read_tsv("lox_hosp_cons_export.csv",
              names=["date","plant","hospital_city","hospital_name","consumption_tons"],
              header=0)
df["_source"] = "lox_hosp_cons_export"
df.to_parquet(BRONZE / "hospital_consumption.parquet", index=False)
print(f"  hospital_consumption: {len(df):,} rows")

# Truck data
df = read_tsv("lox_truck.csv",
              names=["truck","plant","max_capacity","flat_fare","pct_delivery","delivery_tons","total"],
              header=0)
df["_source"] = "lox_truck"
df.to_parquet(BRONZE / "truck_data.parquet", index=False)
print(f"  truck_data: {len(df):,} rows")


# ══ SILVER ════════════════════════════════════════════════════════════════════

print("\n── SILVER ──────────────────────────────────────────────────────────────")

# Plants production
raw = pd.read_parquet(BRONZE / "plants_production.parquet")
raw["date"] = pd.to_datetime(raw["date"].str.strip(), format="%d/%m/%Y %H:%M", errors="coerce")
raw["date"] = raw["date"].dt.normalize()
raw["production_tons"] = raw["production_tons"].apply(eu_float)
raw["stored_tons"]     = raw["stored_tons"].apply(eu_float)
raw["delivered_tons"]  = raw["delivered_tons"].apply(eu_float)
raw["plant"] = raw["plant"].str.strip().str.title()
silver_prod = raw.dropna(subset=["date"]).rename(columns={"date": "date"})
silver_prod.to_parquet(SILVER / "plants_production.parquet", index=False)
print(f"  plants_production: {len(silver_prod):,} rows")

# Plants data
raw = pd.read_parquet(BRONZE / "plants_data.parquet")
for c in ["max_daily_prod","max_storage","cost_energy","other_cost","fixed_monthly_cost"]:
    raw[c] = raw[c].apply(eu_float)
raw["prod_eff"]     = raw["prod_eff"].str.replace("%","").apply(eu_float) / 100
raw["storage_eff"]  = raw["storage_eff"].str.replace("%","").apply(eu_float) / 100
raw["plant"] = raw["plant"].str.strip().str.title()
raw.to_parquet(SILVER / "plants_data.parquet", index=False)
print(f"  plants_data: {len(raw):,} rows")

# LOX delivery
raw = pd.read_parquet(BRONZE / "lox_delivery.parquet")
raw["date"] = pd.to_datetime(
    raw["date"].str.strip().str.replace(r"\s{2,}", " ", regex=True),
    format="%d/%m/%Y %H:%M", errors="coerce"
).dt.normalize()
for c in ["refill_tons","delivery_cost","product_price","total_bill"]:
    raw[c] = raw[c].apply(eu_float)
raw["hospital_name"] = raw["hospital_name"].str.strip().str.title()
raw["hospital_city"] = raw["hospital_city"].str.strip().str.title()
silver_del = raw.dropna(subset=["date","refill_tons"])
silver_del.to_parquet(SILVER / "lox_delivery.parquet", index=False)
print(f"  lox_delivery: {len(silver_del):,} rows")

# Hospital data
raw = pd.read_parquet(BRONZE / "hospital_data.parquet")
raw["storage_capacity_tons"] = raw["storage_capacity_tons"].apply(eu_float)
raw["price_per_ton"]         = raw["price_per_ton"].apply(eu_float)
raw["min_refill_pct"]        = raw["min_refill_pct"].str.replace("%","").apply(eu_float) / 100
raw["hospital_name"] = raw["hospital_name"].str.strip().str.title()
raw["hospital_city"] = raw["hospital_city"].str.strip().str.title()
raw.to_parquet(SILVER / "hospital_data.parquet", index=False)
print(f"  hospital_data: {len(raw):,} rows")

# Hospital consumption - aggregate to daily
raw = pd.read_parquet(BRONZE / "hospital_consumption.parquet")
raw["date"] = pd.to_datetime(raw["date"].str.strip(), format="%d/%m/%Y", errors="coerce").dt.normalize()
raw["consumption_tons"] = raw["consumption_tons"].apply(eu_float)
raw["hospital_name"] = raw["hospital_name"].str.strip().str.title()
raw["hospital_city"] = raw["hospital_city"].str.strip().str.title()
raw["plant"] = raw["plant"].str.strip().str.title()
daily_cons = (
    raw.dropna(subset=["date","consumption_tons"])
    .groupby(["date","plant","hospital_city","hospital_name"], as_index=False)
    ["consumption_tons"].sum()
    .rename(columns={"consumption_tons": "daily_consumption_tons"})
)
daily_cons.to_parquet(SILVER / "hospital_consumption.parquet", index=False)
print(f"  hospital_consumption: {len(daily_cons):,} rows")

# Truck data
raw = pd.read_parquet(BRONZE / "truck_data.parquet")
raw["max_capacity"]  = raw["max_capacity"].apply(eu_float)
raw["flat_fare"]     = raw["flat_fare"].apply(eu_float)
raw["plant"] = raw["plant"].str.strip().str.title()
raw.to_parquet(SILVER / "truck_data.parquet", index=False)
print(f"  truck_data: {len(raw):,} rows")


# ══ GOLD ══════════════════════════════════════════════════════════════════════

print("\n── GOLD ────────────────────────────────────────────────────────────────")

prod   = pd.read_parquet(SILVER / "plants_production.parquet")
plants = pd.read_parquet(SILVER / "plants_data.parquet")
deliv  = pd.read_parquet(SILVER / "lox_delivery.parquet")
hosp   = pd.read_parquet(SILVER / "hospital_data.parquet")
cons   = pd.read_parquet(SILVER / "hospital_consumption.parquet")
trucks = pd.read_parquet(SILVER / "truck_data.parquet")

# dim_date
all_dates = pd.concat([prod["date"], deliv["date"], cons["date"]]).dropna().unique()
dim_date = pd.DataFrame({"date": pd.to_datetime(all_dates)}).sort_values("date")
dim_date["date_key"]    = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"]        = dim_date["date"].dt.year
dim_date["month"]       = dim_date["date"].dt.month
dim_date["day"]         = dim_date["date"].dt.day
dim_date["quarter"]     = dim_date["date"].dt.quarter
dim_date["week"]        = dim_date["date"].dt.isocalendar().week.astype(int)
dim_date["day_of_week"] = dim_date["date"].dt.dayofweek
dim_date["is_weekend"]  = dim_date["day_of_week"].isin([5, 6])
dim_date["month_name"]  = dim_date["date"].dt.strftime("%B")
dim_date.to_parquet(GOLD / "dim_date.parquet", index=False)
print(f"  dim_date: {len(dim_date):,} rows")

# dim_plant
dim_plant = plants.copy().reset_index(drop=True)
dim_plant["plant_key"] = dim_plant.index
dim_plant.to_parquet(GOLD / "dim_plant.parquet", index=False)
print(f"  dim_plant: {len(dim_plant):,} rows")

# dim_hospital
dim_hosp = hosp.copy().reset_index(drop=True)
dim_hosp["hospital_key"] = dim_hosp.index
dim_hosp.to_parquet(GOLD / "dim_hospital.parquet", index=False)
print(f"  dim_hospital: {len(dim_hosp):,} rows")

# dim_truck
dim_truck = trucks.copy().reset_index(drop=True)
dim_truck["truck_key"] = dim_truck.index
dim_truck.to_parquet(GOLD / "dim_truck.parquet", index=False)
print(f"  dim_truck: {len(dim_truck):,} rows")

# fact_production
fact_prod = prod.merge(dim_plant[["plant","plant_key"]], on="plant", how="left")
fact_prod["date_key"] = pd.to_datetime(fact_prod["date"]).dt.strftime("%Y%m%d").astype(int)
fact_prod["utilisation_pct"] = fact_prod["production_tons"] / 4.0
fact_prod.to_parquet(GOLD / "fact_production.parquet", index=False)
print(f"  fact_production: {len(fact_prod):,} rows")

# fact_delivery
fact_del = deliv.merge(dim_hosp[["hospital_name","hospital_key"]], on="hospital_name", how="left")
fact_del = fact_del.merge(dim_truck[["truck","truck_key"]], on="truck", how="left")
fact_del["date_key"] = pd.to_datetime(fact_del["date"]).dt.strftime("%Y%m%d").astype(int)
fact_del["margin"] = fact_del["total_bill"] - fact_del["delivery_cost"] - fact_del["product_price"]
fact_del.to_parquet(GOLD / "fact_delivery.parquet", index=False)
print(f"  fact_delivery: {len(fact_del):,} rows")

# fact_consumption
fact_cons = cons.merge(dim_hosp[["hospital_name","hospital_key"]], on="hospital_name", how="left")
fact_cons["date_key"] = pd.to_datetime(fact_cons["date"]).dt.strftime("%Y%m%d").astype(int)
fact_cons.to_parquet(GOLD / "fact_consumption.parquet", index=False)
print(f"  fact_consumption: {len(fact_cons):,} rows")

# mart_dryout_risk
cons_r = fact_cons.merge(
    hosp[["hospital_name","storage_capacity_tons","min_refill_pct","price_per_ton"]],
    on="hospital_name", how="left"
)
daily_refill = (
    fact_del.groupby(["date","hospital_name"])["refill_tons"]
    .sum().reset_index().rename(columns={"refill_tons":"daily_refill_tons"})
)
merged = cons_r.merge(daily_refill, on=["date","hospital_name"], how="left")
merged["daily_refill_tons"] = merged["daily_refill_tons"].fillna(0)
merged["net_change"] = merged["daily_refill_tons"] - merged["daily_consumption_tons"]
merged = merged.sort_values(["hospital_name","date"])
merged["cumulative_net"] = merged.groupby("hospital_name")["net_change"].cumsum()
merged["estimated_storage"] = (merged["storage_capacity_tons"] + merged["cumulative_net"]).clip(lower=0, upper=None)
merged["estimated_storage"] = merged.apply(
    lambda r: min(r["estimated_storage"], r["storage_capacity_tons"]), axis=1
)
merged["fill_pct"]   = merged["estimated_storage"] / merged["storage_capacity_tons"]
merged["risk_score"] = 1 - merged["fill_pct"]
merged["risk_level"] = merged.apply(
    lambda r: "CRITICAL" if r["fill_pct"] < r["min_refill_pct"]
              else ("HIGH" if r["fill_pct"] < r["min_refill_pct"] * 2
              else ("MEDIUM" if r["fill_pct"] < 0.5 else "LOW")),
    axis=1
)
merged["days_to_dryout"] = merged.apply(
    lambda r: r["estimated_storage"] / r["daily_consumption_tons"]
              if r["daily_consumption_tons"] > 0 else 999.0,
    axis=1
)
merged.to_parquet(GOLD / "mart_dryout_risk.parquet", index=False)
print(f"  mart_dryout_risk: {len(merged):,} rows")
critical_count = (merged["risk_level"] == "CRITICAL").sum()
print(f"    CRITICAL risk events: {critical_count:,}")

# mart_financial
fact_prod["year_month"] = pd.to_datetime(fact_prod["date"]).dt.strftime("%Y-%m")
monthly_prod = (
    fact_prod.merge(plants, on="plant", how="left")
    .groupby(["year_month","plant"])
    .agg(
        total_production_tons=("production_tons","sum"),
        avg_utilisation=("utilisation_pct","mean"),
        fixed_monthly_cost=("fixed_monthly_cost","first"),
        cost_energy=("cost_energy","first"),
        other_cost=("other_cost","first"),
    ).reset_index()
)
monthly_prod["variable_cost"] = monthly_prod["total_production_tons"] * (
    monthly_prod["cost_energy"] + monthly_prod["other_cost"]
)
monthly_prod["total_cost"] = monthly_prod["variable_cost"] + monthly_prod["fixed_monthly_cost"]

truck_plant = trucks[["truck","plant"]]
fact_del["year_month"] = pd.to_datetime(fact_del["date"]).dt.strftime("%Y-%m")
fact_del_with_plant = fact_del.merge(truck_plant, on="truck", how="left", suffixes=("","_truck"))
if "plant_truck" in fact_del_with_plant.columns:
    fact_del_with_plant["plant"] = fact_del_with_plant["plant_truck"].fillna(fact_del_with_plant["plant"])
monthly_rev = (
    fact_del_with_plant.groupby(["year_month","plant"])["total_bill"]
    .sum().reset_index().rename(columns={"total_bill":"total_revenue"})
)
mart_fin = monthly_prod.merge(monthly_rev, on=["year_month","plant"], how="left")
mart_fin["total_revenue"] = mart_fin["total_revenue"].fillna(0)
mart_fin["gross_margin"]  = mart_fin["total_revenue"] - mart_fin["total_cost"]
mart_fin["margin_pct"]    = mart_fin["gross_margin"] / mart_fin["total_revenue"].replace(0, np.nan)
mart_fin = mart_fin.sort_values(["year_month","plant"])
mart_fin.to_parquet(GOLD / "mart_financial.parquet", index=False)
print(f"  mart_financial: {len(mart_fin):,} rows")

print("\n✓ Full pipeline complete. Gold data written to data/gold/")
