import streamlit as st
import psycopg2
import pandas as pd

# ---- DB CONFIG ----
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "n8n_db",
    "user": "n8n",
    "password": ".mgok123"
}

@st.cache_data
def load_analysis():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            a.created_at,
            a.asset,
            a.sentiment,
            a.impact_score,
            a.summary,
            n.source,
            n.published_at
        FROM analysis a
        LEFT JOIN news n ON n.id = a.news_id
        ORDER BY a.created_at DESC
        LIMIT 50;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---- UI ----
st.set_page_config(page_title="AI Market Intelligence", layout="wide")

st.title("📊 AI Market Intelligence Dashboard")

df = load_analysis()

asset_filter = st.selectbox(
    "Varlık seç",
    options=["All"] + sorted(df["asset"].dropna().unique().tolist())
)

if asset_filter != "All":
    df = df[df["asset"] == asset_filter]

st.dataframe(df, use_container_width=True)

