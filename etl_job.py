import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

# Get DB connection info from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "taxi_db")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASS = os.environ.get("DB_PASS", "admin")

# JDBC URL
jdbc_url = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Spark session
spark = SparkSession.builder \
    .appName("NYC Taxi ETL") \
    .config("spark.jars", "jars/postgresql-42.6.2.jar") \
    .getOrCreate()

# Load Parquet file
df = spark.read.parquet("data/yellow_tripdata_2025-01.parquet")

# Clean and transform
df_clean = df.withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
             .select("pickup_date", "passenger_count", "trip_distance", "total_amount") \
             .filter(col("trip_distance") > 0)

# Aggregation
agg_df = df_clean.groupBy("pickup_date") \
    .avg("trip_distance", "total_amount") \
    .withColumnRenamed("avg(trip_distance)", "avg_trip_distance") \
    .withColumnRenamed("avg(total_amount)", "avg_total_amount")

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