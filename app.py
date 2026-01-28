import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="AI Market Dashboard", layout="wide")

# =========================
# DATABASE CONNECTION
# =========================
def get_conn():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=6543,
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10
    )


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_analysis():
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT
            a.created_at,
            a.asset,
            a.sentiment,
            a.impact_score,
            a.summary,
            n.title
        FROM analysis a
        LEFT JOIN news n ON n.id = a.news_id
        ORDER BY a.created_at DESC
        LIMIT 100
        """,
        conn
    )
    conn.close()
    return df

# =========================
# UI
# =========================
st.title("📊 AI Market Intelligence Dashboard")

df = load_analysis()

st.subheader("🧠 Latest AI Analysis")
st.dataframe(df, use_container_width=True)

st.subheader("📈 Impact Score by Asset")
chart_df = df[["created_at", "asset", "impact_score"]].dropna()
st.line_chart(chart_df, x="created_at", y="impact_score", color="asset")
