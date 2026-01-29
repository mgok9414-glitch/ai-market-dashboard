import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# =========================
# DATABASE CONFIG (FINAL)
# =========================
DB_CONFIG = {
    "host": "aws-1-eu-central-1.pooler.supabase.com",
    "port": 6543,  # transaction pooling
    "dbname": "postgres",
    "user": "postgres.eczwohofchcczicmtlsp",
    "password": st.secrets["DB_PASSWORD"],
    "sslmode": "require"
}

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_analysis():
    conn = psycopg2.connect(**DB_CONFIG)

    df = pd.read_sql(
        """
        SELECT
            asset,
            impact_score,
            sentiment,
            summary,
            created_at
        FROM analysis
        ORDER BY created_at DESC
        """,
        conn
    )

    conn.close()
    return df

# =========================
# UI
# =========================
st.set_page_config(page_title="AI Market Dashboard", layout="wide")
st.title("📊 AI Market Dashboard")

df = load_analysis()

st.dataframe(df, use_container_width=True)
