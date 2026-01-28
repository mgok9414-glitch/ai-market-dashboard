import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# --------------------
# DATABASE CONFIG
# --------------------
DB_CONFIG = {
    "host": "aws-0-eu-central-1.pooler.supabase.com",
    "port": 6543,
    "dbname": "postgres",
    "user": "postgres.eczwohofchcczicmtlsp",
    "password": st.secrets["DB_PASSWORD"],
    "sslmode": "require"
}

# --------------------
# LOAD DATA
# --------------------
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

# --------------------
# APP UI
# --------------------
st.set_page_config(page_title="AI Market Dashboard", layout="wide")
st.title("📊 AI Market Dashboard")

df = load_analysis()

if df.empty:
    st.warning("Henüz analiz verisi yok.")
    st.stop()

# --------------------
# FILTERS
# --------------------
st.subheader("🔎 Filters")

assets = st.multiselect(
    "Select assets",
    options=sorted(df["asset"].unique()),
    default=sorted(df["asset"].unique())
)

df = df[df["asset"].isin(assets)]

# --------------------
# TABLE
# --------------------
st.subheader("🧾 Latest AI Analysis")
st.dataframe(df, use_container_width=True)

# --------------------
# IMPACT OVER TIME
# --------------------
st.subheader("📈 Impact Score Over Time")

fig_time = px.line(
    df,
    x="created_at",
    y="impact_score",
    color="asset",
    markers=True
)

st.plotly_chart(fig_time, use_container_width=True)

# --------------------
# AVERAGE IMPACT
# --------------------
st.subheader("📊 Average Impact by Asset")

avg_df = (
    df.groupby("asset", as_index=False)["impact_score"]
    .mean()
    .sort_values("impact_score", ascending=False)
)

fig_avg = px.bar(
    avg_df,
    x="asset",
    y="impact_score",
    color="impact_score",
    text_auto=True
)

st.plotly_chart(fig_avg, use_container_width=True)

# --------------------
# SENTIMENT
# --------------------
st.subheader("🧠 Sentiment Distribution")

fig_sent = px.pie(
    df,
    names="sentiment",
    hole=0.4
)

st.plotly_chart(fig_sent, use_container_width=True)
