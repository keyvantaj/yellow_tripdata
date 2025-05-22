from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

spark = SparkSession.builder \
    .appName("NYC Taxi ETL") \
    .config("spark.jars", "jars/postgresql-42.6.2.jar") \
    .getOrCreate()

# Load CSV
df = spark.read.parquet("data/yellow_tripdata_2025-01.parquet")
df.printSchema()
# Clean/transform
df_clean = df.withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
             .select("pickup_date", "passenger_count", "trip_distance", "total_amount") \
             .filter(col("trip_distance") > 0)

# Aggregation
agg_df = df_clean.groupBy("pickup_date") \
    .avg("trip_distance", "total_amount") \
    .withColumnRenamed("avg(trip_distance)", "avg_trip_distance") \
    .withColumnRenamed("avg(total_amount)", "avg_total_amount")

agg_df.show(10)

# Write to PostgreSQL
agg_df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://host.docker.internal:5432/taxi_db") \
    .option("dbtable", "daily_trip_summary") \
    .option("user", "admin") \
    .option("password", "admin") \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()