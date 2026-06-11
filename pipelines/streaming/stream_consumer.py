from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, BooleanType, TimestampType
)
import os

KAFKA_BROKER  = os.environ.get("KAFKA_BROKER", "kafka:9092")
SILVER_PATH   = os.environ.get("SILVER_PATH", "/opt/spark-data/silver")
GOLD_PATH     = os.environ.get("GOLD_PATH",   "/opt/spark-data/gold")
CHECKPOINT    = os.environ.get("CHECKPOINT",  "/opt/spark-data/checkpoints")


PRODUCTION_SCHEMA = StructType([
    StructField("event_time", StringType()),
    StructField("plant", StringType()),
    StructField("production_rate_tons_per_min", DoubleType()),
    StructField("sensor_ok", BooleanType()),
])

CONSUMPTION_SCHEMA = StructType([
    StructField("event_time", StringType()),
    StructField("hospital_name", StringType()),
    StructField("hospital_city", StringType()),
    StructField("plant", StringType()),
    StructField("consumption_tons_per_min", DoubleType()),
])


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ManOxCo-Streaming-Consumer")
        .config("spark.sql.streaming.schemaInference", "true")
        .getOrCreate()
    )


def read_kafka(spark, topic):
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
        .select(F.col("value").cast("string").alias("json_value"))
    )


def stream_production(spark):
    raw = read_kafka(spark, "manoxco.iot.production")
    parsed = (
        raw
        .select(F.from_json("json_value", PRODUCTION_SCHEMA).alias("data"))
        .select("data.*")
        .withColumn("event_ts", F.to_timestamp("event_time"))
        .filter(F.col("sensor_ok") == True)
        .withWatermark("event_ts", "2 minutes")
    )

    minutely = (
        parsed
        .groupBy(
            F.window("event_ts", "1 minute").alias("window"),
            "plant",
        )
        .agg(F.sum("production_rate_tons_per_min").alias("production_tons_window"))
        .select(
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "plant",
            "production_tons_window",
        )
    )

    return (
        minutely.writeStream
        .outputMode("update")
        .format("parquet")
        .option("path", f"{SILVER_PATH}/stream_production")
        .option("checkpointLocation", f"{CHECKPOINT}/production")
        .trigger(processingTime="30 seconds")
        .start()
    )


def stream_consumption(spark):
    raw = read_kafka(spark, "manoxco.iot.consumption")
    parsed = (
        raw
        .select(F.from_json("json_value", CONSUMPTION_SCHEMA).alias("data"))
        .select("data.*")
        .withColumn("event_ts", F.to_timestamp("event_time"))
        .withWatermark("event_ts", "2 minutes")
    )

    minutely = (
        parsed
        .groupBy(
            F.window("event_ts", "1 minute").alias("window"),
            "hospital_name",
            "hospital_city",
            "plant",
        )
        .agg(F.sum("consumption_tons_per_min").alias("consumption_tons_window"))
        .select(
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "hospital_name",
            "hospital_city",
            "plant",
            "consumption_tons_window",
        )
    )

    return (
        minutely.writeStream
        .outputMode("update")
        .format("parquet")
        .option("path", f"{SILVER_PATH}/stream_consumption")
        .option("checkpointLocation", f"{CHECKPOINT}/consumption")
        .trigger(processingTime="30 seconds")
        .start()
    )


if __name__ == "__main__":
    spark = create_spark_session()
    q1 = stream_production(spark)
    q2 = stream_consumption(spark)
    print("[STREAM] Queries started. Awaiting termination...")
    spark.streams.awaitAnyTermination()
