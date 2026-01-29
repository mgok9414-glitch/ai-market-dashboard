import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Market Dashboard",
    layout="wide"
)

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "aws-1-eu-central-1.pooler.supabase.com",
    "port": 6543,
    "dbname": "postgres",
    "user": "postgres.eczwohofchcczicmtlsp",
    "password": st.secrets["DB_PASSWORD"],
    "sslmode": "require"
}

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=300)
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
    return df@st.cache_data(ttl=300)
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

    # 🔑 KRİTİK SATIR (HATAYI BİTİREN)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df



df = load_analysis()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🔍 Filtreler")

asset_filter = st.sidebar.multiselect(
    "Varlık Seç",
    options=sorted(df["asset"].unique()),
    default=sorted(df["asset"].unique())
)

sentiment_filter = st.sidebar.multiselect(
    "Sentiment",
    options=sorted(df["sentiment"].unique()),
    default=sorted(df["sentiment"].unique())
)

df = df[
    (df["asset"].isin(asset_filter)) &
    (df["sentiment"].isin(sentiment_filter))
]

# =========================
# HEADER METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Toplam Haber",
    len(df)
)

col2.metric(
    "Ortalama Etki Skoru",
    round(df["impact_score"].mean(), 2) if not df.empty else 0
)

col3.metric(
    "Takip Edilen Varlık",
    df["asset"].nunique()
)

st.divider()

# =========================
# IMPACT SCORE OVER TIME
# =========================
if df.empty:
    st.warning("Henüz analiz verisi yok. n8n akışı çalıştıktan sonra grafikler görünecek.")
    st.stop()

st.subheader("📈 Etki Skoru Zaman Serisi")

impact_time = (
    df
    .groupby(pd.Grouper(key="created_at", freq="D"))
    .impact_score
    .mean()
    .reset_index()
)

fig_time = px.line(
    impact_time,
    x="created_at",
    y="impact_score",
    markers=True
)

st.plotly_chart(fig_time, use_container_width=True)

# =========================
# SENTIMENT DISTRIBUTION
# =========================
st.subheader("🧠 Sentiment Dağılımı")

fig_sentiment = px.pie(
    df,
    names="sentiment",
    hole=0.4
)

st.plotly_chart(fig_sentiment, use_container_width=True)

# =========================
# TOP ASSETS BY IMPACT
# =========================
st.subheader("🔥 En Yüksek Etkili Varlıklar")

top_assets = (
    df.groupby("asset")
    .impact_score.mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_assets = px.bar(
    top_assets,
    x="asset",
    y="impact_score"
)

st.plotly_chart(fig_assets, use_container_width=True)

# =========================
# RAW DATA
# =========================
with st.expander("📄 Ham Veriyi Göster"):
    st.dataframe(df, use_container_width=True)
