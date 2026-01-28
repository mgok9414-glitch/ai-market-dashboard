import psycopg2
import streamlit as st
import pandas as pd

DB_CONFIG = {
    "host": "aws-1-eu-central-1.pooler.supabase.com",  # pooler host
    "port": 6543,
    "dbname": "postgres",
    "user": "postgres.eczwohofchcczicmtlsp",
    "password": st.secrets["DB_PASSWORD"],
    "sslmode": "require"
}

@st.cache_data
def load_analysis():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT * FROM analysis ORDER BY created_at DESC", conn)
    conn.close()
    return df

st.title("📊 AI Market Dashboard")
df = load_analysis()
st.dataframe(df)
