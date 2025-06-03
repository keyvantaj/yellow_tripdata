import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, avg


def get_spark_session(app_name="NYC Taxi ETL") -> SparkSession:
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars", "jars/postgresql-42.6.2.jar") \
        .getOrCreate()


def read_data(spark: SparkSession, input_path: str):
    return spark.read.parquet(input_path)


def transform_data(df):
    df_clean = df.withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
                 .select("pickup_date", "passenger_count", "trip_distance", "total_amount") \
                 .filter(col("trip_distance") > 0)

    agg_df = df_clean.groupBy("pickup_date").agg(
        avg("trip_distance").alias("avg_trip_distance"),
        avg("total_amount").alias("avg_total_amount")
    )
    return agg_df


def write_to_postgres(df, jdbc_url, user, password):
    df.write \
      .format("jdbc") \
      .option("url", jdbc_url) \
      .option("dbtable", "daily_trip_summary") \
      .option("user", user) \
      .option("password", password) \
      .option("driver", "org.postgresql.Driver") \
      .mode("overwrite") \
      .save()


def run_etl():
    # Load env vars
    DB_HOST = os.environ.get("DB_HOST", "postgres")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "taxi_db")
    DB_USER = os.environ.get("DB_USER", "admin")
    DB_PASS = os.environ.get("DB_PASS", "admin")

    input_path = "/data/yellow_tripdata_2025-01.parquet"
    jdbc_url = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

    spark = get_spark_session()
    df_raw = read_data(spark, input_path)
    agg_df = transform_data(df_raw)

    # Optional validation
    result = agg_df.collect()
    assert all(r["avg_trip_distance"] > 0 for r in result)

    write_to_postgres(agg_df, jdbc_url, DB_USER, DB_PASS)

    spark.stop()
    
if __name__ == "__main__":
    run_etl()