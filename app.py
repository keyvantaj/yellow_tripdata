import streamlit as st
import pandas as pd
import psycopg2

st.title("NYC Taxi Trip Summary")

# Connect to PostgreSQL (running in Docker)
conn = psycopg2.connect(
    host="postgres",
    port=5432,
    dbname="taxi_db",
    user="admin",
    password="admin"
)

query = "SELECT * FROM daily_trip_summary ORDER BY pickup_date LIMIT 100;"
df = pd.read_sql(query, conn)

st.subheader("Daily Trip Summary (first 100 rows)")
st.dataframe(df)

if st.checkbox("Show aggregated stats"):
    st.write(df.describe())

conn.close()