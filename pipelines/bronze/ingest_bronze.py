from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, input_file_name
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, DateType, TimestampType
)
import os
from datetime import datetime

DATA_SOURCE = os.environ.get("DATA_SOURCE", "/opt/spark-data/data_source")
BRONZE_PATH = os.environ.get("BRONZE_PATH", "/opt/spark-data/bronze")


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ManOxCo-Bronze-Ingestion")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )


def add_metadata(df, source_name):
    return (
        df
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_file", lit(source_name))
        .withColumn("_batch_id", lit(datetime.utcnow().strftime("%Y%m%d%H%M%S")))
    )


def ingest_plants_production(spark):
    schema = StructType([
        StructField("date", StringType(), True),
        StructField("plant", StringType(), True),
        StructField("production_tons", StringType(), True),
        StructField("stored_tons", StringType(), True),
        StructField("delivered_tons", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/plants_production_export.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "plants_production_export")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/plants_production")
    print(f"[BRONZE] plants_production: {df.count()} rows")


def ingest_plants_data(spark):
    schema = StructType([
        StructField("plant", StringType(), True),
        StructField("max_daily_production_tons", StringType(), True),
        StructField("max_lox_storage_capacity_tons", StringType(), True),
        StructField("plant_avg_production_efficiency", StringType(), True),
        StructField("plant_avg_storage_efficiency", StringType(), True),
        StructField("cost_energy_per_ton", StringType(), True),
        StructField("other_cost_per_ton", StringType(), True),
        StructField("fixed_monthly_cost", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/plants_data.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "plants_data")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/plants_data")
    print(f"[BRONZE] plants_data: {df.count()} rows")


def ingest_lox_delivery(spark):
    schema = StructType([
        StructField("date", StringType(), True),
        StructField("truck", StringType(), True),
        StructField("hospital_city", StringType(), True),
        StructField("hospital_name", StringType(), True),
        StructField("refill_tons", StringType(), True),
        StructField("delivery_cost", StringType(), True),
        StructField("product_tot_price", StringType(), True),
        StructField("total_bill", StringType(), True),
        StructField("over_delivery", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/lox_delivery_export.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "lox_delivery_export")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/lox_delivery")
    print(f"[BRONZE] lox_delivery: {df.count()} rows")


def ingest_hospital_data(spark):
    schema = StructType([
        StructField("hospital_city", StringType(), True),
        StructField("hospital_name", StringType(), True),
        StructField("storage_max_capacity_tons", StringType(), True),
        StructField("min_to_refill_pct", StringType(), True),
        StructField("price_per_ton", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/lox_hosp_data.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "lox_hosp_data")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/hospital_data")
    print(f"[BRONZE] hospital_data: {df.count()} rows")


def ingest_hospital_consumption(spark):
    schema = StructType([
        StructField("date", StringType(), True),
        StructField("plant", StringType(), True),
        StructField("hospital_city", StringType(), True),
        StructField("hospital_name", StringType(), True),
        StructField("consumption_tons", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/lox_hosp_cons_export.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "lox_hosp_cons_export")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/hospital_consumption")
    print(f"[BRONZE] hospital_consumption: {df.count()} rows")


def ingest_truck_data(spark):
    schema = StructType([
        StructField("truck", StringType(), True),
        StructField("plant", StringType(), True),
        StructField("max_capacity", StringType(), True),
        StructField("flat_delivery_fare", StringType(), True),
        StructField("pct_delivery_in_tons", StringType(), True),
        StructField("delivery_in_tons", StringType(), True),
        StructField("total", StringType(), True),
    ])
    path = f"{DATA_SOURCE}/lox_truck.csv"
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", "true")
        .option("encoding", "ISO-8859-1")
        .schema(schema)
        .csv(path)
    )
    df = add_metadata(df, "lox_truck")
    df.write.mode("overwrite").parquet(f"{BRONZE_PATH}/truck_data")
    print(f"[BRONZE] truck_data: {df.count()} rows")


if __name__ == "__main__":
    spark = create_spark_session()
    ingest_plants_production(spark)
    ingest_plants_data(spark)
    ingest_lox_delivery(spark)
    ingest_hospital_data(spark)
    ingest_hospital_consumption(spark)
    ingest_truck_data(spark)
    print("[BRONZE] All datasets ingested successfully.")
    spark.stop()
