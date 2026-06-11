from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os

SILVER_PATH = os.environ.get("SILVER_PATH", "/opt/spark-data/silver")
GOLD_PATH   = os.environ.get("GOLD_PATH",   "/opt/spark-data/gold")


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ManOxCo-Gold-Build")
        .getOrCreate()
    )


# ── Dimensions ────────────────────────────────────────────────────────────────

def build_dim_date(spark):
    prod = spark.read.parquet(f"{SILVER_PATH}/plants_production").select("date")
    deliv = spark.read.parquet(f"{SILVER_PATH}/lox_delivery").select("date")
    cons  = spark.read.parquet(f"{SILVER_PATH}/hospital_consumption").select("date")

    dates = prod.union(deliv).union(cons).distinct()

    dim = (
        dates
        .withColumn("date_key", F.date_format("date", "yyyyMMdd").cast("int"))
        .withColumn("year",    F.year("date"))
        .withColumn("month",   F.month("date"))
        .withColumn("day",     F.dayofmonth("date"))
        .withColumn("quarter", F.quarter("date"))
        .withColumn("week",    F.weekofyear("date"))
        .withColumn("day_of_week", F.dayofweek("date"))
        .withColumn("is_weekend", (F.dayofweek("date").isin(1, 7)).cast("boolean"))
        .withColumn("month_name", F.date_format("date", "MMMM"))
    )

    dim.write.mode("overwrite").parquet(f"{GOLD_PATH}/dim_date")
    print(f"[GOLD] dim_date: {dim.count()} rows")


def build_dim_plant(spark):
    plants = spark.read.parquet(f"{SILVER_PATH}/plants_data")
    dim = plants.withColumn("plant_key", F.monotonically_increasing_id())
    dim.write.mode("overwrite").parquet(f"{GOLD_PATH}/dim_plant")
    print(f"[GOLD] dim_plant: {dim.count()} rows")


def build_dim_hospital(spark):
    hosp = spark.read.parquet(f"{SILVER_PATH}/hospital_data")
    dim = hosp.withColumn("hospital_key", F.monotonically_increasing_id())
    dim.write.mode("overwrite").parquet(f"{GOLD_PATH}/dim_hospital")
    print(f"[GOLD] dim_hospital: {dim.count()} rows")


def build_dim_truck(spark):
    trucks = spark.read.parquet(f"{SILVER_PATH}/truck_data")
    dim = trucks.withColumn("truck_key", F.monotonically_increasing_id())
    dim.write.mode("overwrite").parquet(f"{GOLD_PATH}/dim_truck")
    print(f"[GOLD] dim_truck: {dim.count()} rows")


# ── Fact tables ───────────────────────────────────────────────────────────────

def build_fact_production(spark):
    prod   = spark.read.parquet(f"{SILVER_PATH}/plants_production")
    plants = spark.read.parquet(f"{GOLD_PATH}/dim_plant").select("plant", "plant_key")

    fact = (
        prod
        .join(plants, "plant", "left")
        .withColumn("date_key", F.date_format("date", "yyyyMMdd").cast("int"))
        .withColumn("utilisation_pct",
            F.col("production_tons") / F.lit(4.0))  # normalised to max 4t/day
        .select(
            "date_key",
            "plant_key",
            "date",
            "plant",
            "production_tons",
            "stored_tons",
            "delivered_tons",
            "utilisation_pct",
        )
    )

    fact.write.mode("overwrite").partitionBy("plant").parquet(f"{GOLD_PATH}/fact_production")
    print(f"[GOLD] fact_production: {fact.count()} rows")


def build_fact_delivery(spark):
    deliv = spark.read.parquet(f"{SILVER_PATH}/lox_delivery")
    hosp  = spark.read.parquet(f"{GOLD_PATH}/dim_hospital").select("hospital_name", "hospital_key")
    trucks = spark.read.parquet(f"{GOLD_PATH}/dim_truck").select("truck", "truck_key")

    fact = (
        deliv
        .join(hosp,  "hospital_name", "left")
        .join(trucks, "truck", "left")
        .withColumn("date_key", F.date_format("date", "yyyyMMdd").cast("int"))
        .withColumn("margin",
            F.col("total_bill") - F.col("delivery_cost") - F.col("product_price"))
        .select(
            "date_key",
            "hospital_key",
            "truck_key",
            "date",
            "hospital_city",
            "hospital_name",
            "truck",
            "refill_tons",
            "delivery_cost",
            "product_price",
            "total_bill",
            "margin",
            "over_delivery",
        )
    )

    fact.write.mode("overwrite").partitionBy("hospital_city").parquet(f"{GOLD_PATH}/fact_delivery")
    print(f"[GOLD] fact_delivery: {fact.count()} rows")


def build_fact_consumption(spark):
    cons = spark.read.parquet(f"{SILVER_PATH}/hospital_consumption")
    hosp = spark.read.parquet(f"{GOLD_PATH}/dim_hospital").select("hospital_name", "hospital_key")

    # Daily aggregated (source has per-reading rows)
    daily = (
        cons
        .groupBy("date", "plant", "hospital_city", "hospital_name")
        .agg(F.sum("consumption_tons").alias("daily_consumption_tons"))
    )

    fact = (
        daily
        .join(hosp, "hospital_name", "left")
        .withColumn("date_key", F.date_format("date", "yyyyMMdd").cast("int"))
        .select(
            "date_key",
            "hospital_key",
            "date",
            "plant",
            "hospital_city",
            "hospital_name",
            "daily_consumption_tons",
        )
    )

    fact.write.mode("overwrite").partitionBy("hospital_city").parquet(f"{GOLD_PATH}/fact_consumption")
    print(f"[GOLD] fact_consumption: {fact.count()} rows")


# ── Analytical marts ──────────────────────────────────────────────────────────

def build_mart_dryout_risk(spark):
    """
    Computes a rolling dry-out risk score per hospital per day.

    Risk logic:
      1. Estimate current storage = max_capacity - cumulative_consumption since last delivery
      2. Compute fill_pct = estimated_storage / max_capacity
      3. risk_score = 1 - fill_pct  (0 = full, 1 = empty)
      4. Flag CRITICAL if fill_pct < min_refill_pct threshold
    """
    cons  = spark.read.parquet(f"{GOLD_PATH}/fact_consumption")
    deliv = spark.read.parquet(f"{GOLD_PATH}/fact_delivery")
    hosp  = spark.read.parquet(f"{SILVER_PATH}/hospital_data")

    # Aggregate daily refill per hospital
    daily_refill = (
        deliv
        .groupBy("date", "hospital_name")
        .agg(F.sum("refill_tons").alias("daily_refill_tons"))
    )

    # Join consumption with refill and hospital reference
    combined = (
        cons
        .join(daily_refill, ["date", "hospital_name"], "left")
        .join(hosp.select("hospital_name", "storage_capacity", "min_refill_pct"), "hospital_name", "left")
        .fillna({"daily_refill_tons": 0.0})
        .withColumn("net_change",
            F.coalesce(F.col("daily_refill_tons"), F.lit(0.0))
            - F.col("daily_consumption_tons"))
    )

    # Running cumulative net change per hospital (ordered by date)
    w = Window.partitionBy("hospital_name").orderBy("date").rowsBetween(Window.unboundedPreceding, 0)

    risk = (
        combined
        .withColumn("cumulative_net", F.sum("net_change").over(w))
        .withColumn("estimated_storage",
            F.least(
                F.col("storage_capacity") + F.col("cumulative_net"),
                F.col("storage_capacity")
            ))
        .withColumn("estimated_storage",
            F.greatest(F.col("estimated_storage"), F.lit(0.0)))
        .withColumn("fill_pct", F.col("estimated_storage") / F.col("storage_capacity"))
        .withColumn("risk_score", F.lit(1.0) - F.col("fill_pct"))
        .withColumn("risk_level",
            F.when(F.col("fill_pct") < F.col("min_refill_pct"), F.lit("CRITICAL"))
             .when(F.col("fill_pct") < F.col("min_refill_pct") * 2, F.lit("HIGH"))
             .when(F.col("fill_pct") < 0.5, F.lit("MEDIUM"))
             .otherwise(F.lit("LOW")))
        .withColumn("days_to_dryout",
            F.when(F.col("daily_consumption_tons") > 0,
                F.col("estimated_storage") / F.col("daily_consumption_tons"))
             .otherwise(F.lit(999.0)))
        .select(
            "date",
            "hospital_city",
            "hospital_name",
            "plant",
            "daily_consumption_tons",
            "daily_refill_tons",
            "net_change",
            "estimated_storage",
            "storage_capacity",
            "fill_pct",
            "min_refill_pct",
            "risk_score",
            "risk_level",
            "days_to_dryout",
        )
    )

    risk.write.mode("overwrite").partitionBy("hospital_city").parquet(f"{GOLD_PATH}/mart_dryout_risk")
    print(f"[GOLD] mart_dryout_risk: {risk.count()} rows")
    critical = risk.filter(F.col("risk_level") == "CRITICAL").count()
    print(f"[GOLD]   CRITICAL risk events: {critical}")


def build_mart_financial(spark):
    """
    Monthly cost/revenue/margin summary per plant.
    Joins production costs (from plants_data) with delivery revenue.
    """
    prod   = spark.read.parquet(f"{GOLD_PATH}/fact_production")
    deliv  = spark.read.parquet(f"{GOLD_PATH}/fact_delivery")
    plants = spark.read.parquet(f"{SILVER_PATH}/plants_data")

    monthly_prod = (
        prod
        .withColumn("year_month", F.date_format("date", "yyyy-MM"))
        .groupBy("year_month", "plant")
        .agg(
            F.sum("production_tons").alias("total_production_tons"),
            F.avg("utilisation_pct").alias("avg_utilisation"),
        )
        .join(plants, "plant", "left")
        .withColumn("variable_cost",
            F.col("total_production_tons") * (F.col("cost_energy") + F.col("other_cost")))
        .withColumn("total_cost",
            F.col("variable_cost") + F.col("fixed_monthly_cost"))
    )

    # Revenue is accrued per delivery plant; map truck → plant via truck_data
    truck_plant = spark.read.parquet(f"{SILVER_PATH}/truck_data").select("truck", "plant")
    monthly_rev = (
        deliv
        .join(truck_plant, "truck", "left")
        .withColumn("year_month", F.date_format("date", "yyyy-MM"))
        .groupBy("year_month", "plant")
        .agg(F.sum("total_bill").alias("total_revenue"))
    )

    mart = (
        monthly_prod
        .join(monthly_rev, ["year_month", "plant"], "left")
        .fillna({"total_revenue": 0.0})
        .withColumn("gross_margin", F.col("total_revenue") - F.col("total_cost"))
        .withColumn("margin_pct",
            F.when(F.col("total_revenue") > 0,
                F.col("gross_margin") / F.col("total_revenue"))
             .otherwise(F.lit(0.0)))
        .select(
            "year_month",
            "plant",
            "total_production_tons",
            "avg_utilisation",
            "variable_cost",
            "fixed_monthly_cost",
            "total_cost",
            "total_revenue",
            "gross_margin",
            "margin_pct",
        )
        .orderBy("year_month", "plant")
    )

    mart.write.mode("overwrite").parquet(f"{GOLD_PATH}/mart_financial")
    print(f"[GOLD] mart_financial: {mart.count()} rows")


if __name__ == "__main__":
    spark = create_spark_session()
    build_dim_date(spark)
    build_dim_plant(spark)
    build_dim_hospital(spark)
    build_dim_truck(spark)
    build_fact_production(spark)
    build_fact_delivery(spark)
    build_fact_consumption(spark)
    build_mart_dryout_risk(spark)
    build_mart_financial(spark)
    print("[GOLD] All Gold tables built successfully.")
    spark.stop()
