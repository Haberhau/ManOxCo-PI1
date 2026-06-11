from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, DateType
import os

BRONZE_PATH = os.environ.get("BRONZE_PATH", "/opt/spark-data/bronze")
SILVER_PATH = os.environ.get("SILVER_PATH", "/opt/spark-data/silver")


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ManOxCo-Silver-Transform")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )


def eu_to_double(col_name):
    """Convert European decimal string '1.234,56' → double 1234.56."""
    return (
        F.regexp_replace(F.regexp_replace(F.col(col_name), r"\.", ""), ",", ".")
        .cast(DoubleType())
    )


def clean_plant_name(col_name):
    return F.initcap(F.trim(F.col(col_name)))


# ── Plants production ─────────────────────────────────────────────────────────

def transform_plants_production(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/plants_production")

    df = (
        df
        .withColumn("date_parsed",
            F.to_timestamp(F.trim(F.col("date")), "dd/MM/yyyy HH:mm"))
        .withColumn("date_day", F.to_date("date_parsed"))
        .withColumn("production_tons_d", eu_to_double("production_tons"))
        .withColumn("stored_tons_d", eu_to_double("stored_tons"))
        .withColumn("delivered_tons_d", eu_to_double("delivered_tons"))
        .withColumn("plant_clean", clean_plant_name("plant"))
        .filter(F.col("date_day").isNotNull())
        .select(
            F.col("date_day").alias("date"),
            F.col("plant_clean").alias("plant"),
            F.col("production_tons_d").alias("production_tons"),
            F.col("stored_tons_d").alias("stored_tons"),
            F.col("delivered_tons_d").alias("delivered_tons"),
            "_ingested_at",
            "_batch_id",
        )
    )

    df.write.mode("overwrite").partitionBy("plant").parquet(f"{SILVER_PATH}/plants_production")
    print(f"[SILVER] plants_production: {df.count()} rows")


# ── Plants data (reference) ───────────────────────────────────────────────────

def transform_plants_data(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/plants_data")

    df = (
        df
        .withColumn("plant_clean", clean_plant_name("plant"))
        .withColumn("max_daily_prod", eu_to_double("max_daily_production_tons"))
        .withColumn("max_storage", eu_to_double("max_lox_storage_capacity_tons"))
        .withColumn("prod_efficiency",
            eu_to_double("plant_avg_production_efficiency") / 100)
        .withColumn("storage_efficiency",
            eu_to_double("plant_avg_storage_efficiency") / 100)
        .withColumn("cost_energy", eu_to_double("cost_energy_per_ton"))
        .withColumn("other_cost", eu_to_double("other_cost_per_ton"))
        .withColumn("fixed_monthly_cost", eu_to_double("fixed_monthly_cost"))
        .select(
            F.col("plant_clean").alias("plant"),
            "max_daily_prod",
            "max_storage",
            "prod_efficiency",
            "storage_efficiency",
            "cost_energy",
            "other_cost",
            "fixed_monthly_cost",
        )
    )

    df.write.mode("overwrite").parquet(f"{SILVER_PATH}/plants_data")
    print(f"[SILVER] plants_data: {df.count()} rows")


# ── LOX delivery ──────────────────────────────────────────────────────────────

def transform_lox_delivery(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/lox_delivery")

    df = (
        df
        .withColumn("date_parsed",
            F.to_timestamp(
                F.trim(F.regexp_replace(F.col("date"), r"\s{2,}", " ")),
                "dd/MM/yyyy HH:mm"
            )
        )
        .withColumn("date_day", F.to_date("date_parsed"))
        .withColumn("refill_tons_d", eu_to_double("refill_tons"))
        .withColumn("delivery_cost_d", eu_to_double("delivery_cost"))
        .withColumn("product_price_d", eu_to_double("product_tot_price"))
        .withColumn("total_bill_d", eu_to_double("total_bill"))
        .withColumn("hospital_name_clean", F.initcap(F.trim(F.col("hospital_name"))))
        .withColumn("hospital_city_clean", F.initcap(F.trim(F.col("hospital_city"))))
        .withColumn("truck_clean", F.trim(F.col("truck")))
        .filter(F.col("date_day").isNotNull() & F.col("refill_tons_d").isNotNull())
        .select(
            F.col("date_day").alias("date"),
            F.col("truck_clean").alias("truck"),
            F.col("hospital_city_clean").alias("hospital_city"),
            F.col("hospital_name_clean").alias("hospital_name"),
            F.col("refill_tons_d").alias("refill_tons"),
            F.col("delivery_cost_d").alias("delivery_cost"),
            F.col("product_price_d").alias("product_price"),
            F.col("total_bill_d").alias("total_bill"),
            F.col("over_delivery"),
            "_ingested_at",
            "_batch_id",
        )
    )

    df.write.mode("overwrite").partitionBy("hospital_city").parquet(f"{SILVER_PATH}/lox_delivery")
    print(f"[SILVER] lox_delivery: {df.count()} rows")


# ── Hospital reference data ───────────────────────────────────────────────────

def transform_hospital_data(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/hospital_data")

    df = (
        df
        .withColumn("hospital_name_clean", F.initcap(F.trim(F.col("hospital_name"))))
        .withColumn("hospital_city_clean", F.initcap(F.trim(F.col("hospital_city"))))
        .withColumn("storage_capacity", eu_to_double("storage_max_capacity_tons"))
        .withColumn("min_refill_pct",
            F.regexp_replace(F.col("min_to_refill_pct"), "%", "").cast(DoubleType()) / 100)
        .withColumn("price_per_ton", eu_to_double("price_per_ton"))
        .select(
            F.col("hospital_city_clean").alias("hospital_city"),
            F.col("hospital_name_clean").alias("hospital_name"),
            "storage_capacity",
            "min_refill_pct",
            "price_per_ton",
        )
    )

    df.write.mode("overwrite").parquet(f"{SILVER_PATH}/hospital_data")
    print(f"[SILVER] hospital_data: {df.count()} rows")


# ── Hospital consumption ──────────────────────────────────────────────────────

def transform_hospital_consumption(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/hospital_consumption")

    df = (
        df
        .withColumn("date_day", F.to_date(F.trim(F.col("date")), "dd/MM/yyyy"))
        .withColumn("consumption_d", eu_to_double("consumption_tons"))
        .withColumn("hospital_name_clean", F.initcap(F.trim(F.col("hospital_name"))))
        .withColumn("hospital_city_clean", F.initcap(F.trim(F.col("hospital_city"))))
        .withColumn("plant_clean", clean_plant_name("plant"))
        .filter(F.col("date_day").isNotNull() & F.col("consumption_d").isNotNull())
        .select(
            F.col("date_day").alias("date"),
            F.col("plant_clean").alias("plant"),
            F.col("hospital_city_clean").alias("hospital_city"),
            F.col("hospital_name_clean").alias("hospital_name"),
            F.col("consumption_d").alias("consumption_tons"),
            "_ingested_at",
            "_batch_id",
        )
    )

    df.write.mode("overwrite").partitionBy("hospital_city").parquet(f"{SILVER_PATH}/hospital_consumption")
    print(f"[SILVER] hospital_consumption: {df.count()} rows")


# ── Truck data ────────────────────────────────────────────────────────────────

def transform_truck_data(spark):
    df = spark.read.parquet(f"{BRONZE_PATH}/truck_data")

    df = (
        df
        .withColumn("plant_clean", clean_plant_name("plant"))
        .withColumn("max_capacity_d", eu_to_double("max_capacity"))
        .withColumn("flat_fare_d", eu_to_double("flat_delivery_fare"))
        .select(
            F.col("truck"),
            F.col("plant_clean").alias("plant"),
            F.col("max_capacity_d").alias("max_capacity_tons"),
            F.col("flat_fare_d").alias("flat_delivery_fare"),
        )
    )

    df.write.mode("overwrite").parquet(f"{SILVER_PATH}/truck_data")
    print(f"[SILVER] truck_data: {df.count()} rows")


if __name__ == "__main__":
    spark = create_spark_session()
    transform_plants_production(spark)
    transform_plants_data(spark)
    transform_lox_delivery(spark)
    transform_hospital_data(spark)
    transform_hospital_consumption(spark)
    transform_truck_data(spark)
    print("[SILVER] All transformations complete.")
    spark.stop()
