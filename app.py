import streamlit as st
import pandas as pd
import psycopg2
import os

st.title("NYC Taxi Trip Summary")

@st.cache_data
def load_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=5432,
            dbname="taxi_db",
            user="admin",
            password="admin"
        )
        query = "SELECT * FROM daily_trip_summary ORDER BY pickup_date LIMIT 100;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data loaded.")
else:
    st.subheader("Daily Trip Summary (first 100 rows)")
    st.dataframe(df)

    if st.checkbox("Show aggregated stats"):
        st.write(df.describe())