import streamlit as st
import pandas as pd
import psycopg2
import json

st.set_page_config(page_title="AI Market Dashboard", layout="wide")

# ========================
# DATABASE CONNECTION
# ========================

conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    port=st.secrets["DB_PORT"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"]
)

# ========================
# LOAD DATA
# ========================

@st.cache_data
def load_analysis():

    query = """
    SELECT
        id,
        summary,
        affected_assets,
        risk_notes,
        model,
        created_at
    FROM public.analysis
    ORDER BY created_at DESC
    """

    df = pd.read_sql(query, conn)
    return df


df = load_analysis()

if df.empty:
    st.warning("Henüz analiz verisi yok.")
    st.stop()

# ========================
# HEADER
# ========================

st.title("📊 AI Piyasa Analiz Dashboard")

latest = df.iloc[0]

# ========================
# FILTER - ASSET DROPDOWN
# ========================

assets_rows = []

for _, row in df.iterrows():

    if row["affected_assets"] is None:
        continue

    assets = row["affected_assets"]

    if isinstance(assets, str):
        assets = json.loads(assets)

    for asset in assets:
        assets_rows.append({
            "asset": asset.get("asset"),
            "sentiment": asset.get("sentiment"),
            "impact_score": asset.get("impact_score"),
            "created_at": row["created_at"]
        })

assets_df = pd.DataFrame(assets_rows)

# ========================
# ASSET FILTER UI
# ========================

selected_assets = None

if not assets_df.empty:
    unique_assets = sorted(assets_df["asset"].dropna().unique())

    selected_assets = st.multiselect(
        "🔎 Varlık Filtresi",
        unique_assets,
        default=unique_assets
    )

    assets_df = assets_df[assets_df["asset"].isin(selected_assets)]

# ========================
# SUMMARY
# ========================

st.subheader("🧠 Son Piyasa Özeti")
st.write(latest["summary"])

# ========================
# GRAPH: IMPACT SCORE
# ========================

if not assets_df.empty:

    st.subheader("📈 Varlık Etki Skorları")

    pivot_df = (
        assets_df
        .pivot_table(
            index="created_at",
            columns="asset",
            values="impact_score",
            aggfunc="mean"
        )
        .sort_index()
    )

    st.line_chart(pivot_df)

# ========================
# SENTIMENT HEATMAP
# ========================

if not assets_df.empty:

    st.subheader("🔥 Sentiment Heatmap")

    sentiment_map = {
        "positive": 1,
        "neutral": 0,
        "negative": -1
    }

    heat_df = assets_df.copy()
    heat_df["sentiment_score"] = heat_df["sentiment"].map(sentiment_map)

    heat_pivot = (
        heat_df
        .pivot_table(
            index="created_at",
            columns="asset",
            values="sentiment_score",
            aggfunc="mean"
        )
        .sort_index()
    )

    st.dataframe(heat_pivot)

# ========================
# DAILY IMPACT METRIC
# ========================

if not assets_df.empty:

    st.subheader("📊 Günlük Ortalama Etki Skoru")

    daily_df = assets_df.copy()
    daily_df["date"] = pd.to_datetime(daily_df["created_at"]).dt.date

    metric_df = (
        daily_df
        .groupby("date")["impact_score"]
        .mean()
        .reset_index()
        .set_index("date")
    )

    st.line_chart(metric_df)

# ========================
# RISK NOTES
# ========================

st.subheader("⚠️ Risk Notları")

risks = latest["risk_notes"]

if isinstance(risks, str):
    risks = json.loads(risks)

for r in risks:
    st.write(f"- {r}")

# ========================
# RAW TABLE
# ========================

st.subheader("📋 Tüm Analiz Kayıtları")
st.dataframe(df)
