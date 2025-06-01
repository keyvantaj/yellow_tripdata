import pytest
from unittest import mock
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[*]").appName("Test ETL").getOrCreate()


def test_etl_transformation(spark):
    # Sample input data
    df = spark.read.parquet("../data/yellow_tripdata_2025-01.parquet")

    # Apply transformations (mimicking etl_job.py logic)
    from pyspark.sql.functions import col, to_date

    # Clean and transform
    df_clean = df.withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
        .select("pickup_date", "passenger_count", "trip_distance", "total_amount") \
        .filter(col("trip_distance") > 0)

    # Aggregation
    agg_df = df_clean.groupBy("pickup_date") \
        .avg("trip_distance", "total_amount") \
        .withColumnRenamed("avg(trip_distance)", "avg_trip_distance") \
        .withColumnRenamed("avg(total_amount)", "avg_total_amount")

    result = agg_df.collect()

    # Verify results
    assert len(result) == 33  # Only two valid dates
    assert all(r["avg_trip_distance"] > 0 for r in result)