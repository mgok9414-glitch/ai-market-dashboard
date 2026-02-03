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

# ========================
# EMPTY CHECK
# ========================

if df.empty:
    st.warning("Henüz analiz verisi yok.")
    st.stop()

# ========================
# HEADER
# ========================

st.title("📊 AI Piyasa Analiz Dashboard")

latest = df.iloc[0]

# ========================
# SUMMARY
# ========================

st.subheader("🧠 Son Piyasa Özeti")
st.write(latest["summary"])

# ========================
# PARSE ASSETS JSON
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
