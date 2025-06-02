import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, avg

# Environment variables with correct defaults
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "taxi_db")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASS = os.environ.get("DB_PASS", "admin")

jdbc_url = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Start Spark session
spark = SparkSession.builder \
    .appName("NYC Taxi ETL") \
    .config("spark.jars", "jars/postgresql-42.6.2.jar") \
    .getOrCreate()

# Read Parquet
df = spark.read.parquet("/data/yellow_tripdata_2025-01.parquet")

# Transform
df_clean = df.withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
             .select("pickup_date", "passenger_count", "trip_distance", "total_amount") \
             .filter(col("trip_distance") > 0)

# Aggregate
agg_df = df_clean.groupBy("pickup_date").agg(
    avg("trip_distance").alias("avg_trip_distance"),
    avg("total_amount").alias("avg_total_amount")
)

# Validation (optional)
result = agg_df.collect()
assert all(r["avg_trip_distance"] > 0 for r in result)

# Write to PostgreSQL
agg_df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "daily_trip_summary") \
    .option("user", DB_USER) \
    .option("password", DB_PASS) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()