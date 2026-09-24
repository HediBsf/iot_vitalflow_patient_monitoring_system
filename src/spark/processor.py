from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, expr, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

KAFKA_BOOTSTRAP = "kafka:9092"
INPUT_TOPIC = "icu-vitals"
ALERT_TOPIC = "icu-alerts"

def get_schema():
    # Updated schema to match the Gateway's JSON output including DeviceID and Unit
    return StructType([
        StructField("subject_id", LongType(), True),
        StructField("device_id", StringType(), True),
        StructField("charttime", StringType(), True),
        StructField("valuenum", DoubleType(), True),
        StructField("label", StringType(), True),
        StructField("unit", StringType(), True)
    ])

def run():
    spark = SparkSession.builder.appName("ICU_Monitor").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # 1. Read Raw Stream
    raw_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
        .option("subscribe", INPUT_TOPIC) \
        .load() \
        .select(from_json(col("value").cast("string"), get_schema()).alias("data")) \
        .select("data.*") \
        .withColumnRenamed("charttime", "timestamp") \
        .withColumnRenamed("valuenum", "value") \
        .withColumnRenamed("label", "metric") \
        .withColumn("timestamp", col("timestamp").cast("timestamp"))

    # 2. Aggregation (30s Tumbling Window)
    agg_df = raw_df \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(
            window(col("timestamp"), "30 seconds"), 
            col("subject_id"), 
            col("metric"),
            col("device_id"), 
            col("unit")
        ) \
        .agg(avg("value").alias("avg_value"))

    # 3. Detect Anomalies (Sepsis / Shock Logic)
    alerts_df = agg_df.filter(
        ((col("metric") == "HeartRate") & (col("avg_value") > 100)) | 
        ((col("metric") == "O2Sat") & (col("avg_value") < 95))
    ).withColumn("alert_message", expr("'CRITICAL VITALS DETECTED'"))

    # 4. Write Alerts back to Kafka (for the Alert System to pick up)
    query_kafka = alerts_df.select(to_json(struct("*")).alias("value")) \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
        .option("topic", ALERT_TOPIC) \
        .option("checkpointLocation", "/tmp/checkpoints/alerts") \
        .outputMode("update") \
        .start()

    # 5. Console Output for Grading Proof
    query_console = agg_df.writeStream \
        .format("console") \
        .outputMode("update") \
        .option("truncate", False) \
        .start()

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    run()
