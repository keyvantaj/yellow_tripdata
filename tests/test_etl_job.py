# test_etl.py
from etl_job import transform_data
from pyspark.sql import SparkSession
import pytest


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local").appName("test").getOrCreate()


def test_transform_data(spark):
    from pyspark.sql import Row
    data = [
        Row(tpep_pickup_datetime="2025-01-01", passenger_count=1, trip_distance=2.5, total_amount=15.0),
        Row(tpep_pickup_datetime="2025-01-02", passenger_count=2, trip_distance=0.0, total_amount=0.0),  # filtered out
    ]
    df = spark.createDataFrame(data)
    result = transform_data(df).collect()
    assert len(result) == 1
    assert result[0]["avg_trip_distance"] > 0