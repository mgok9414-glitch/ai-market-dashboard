import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="AI Market Dashboard", layout="wide")

# -----------------------
# DATABASE CONNECTION
# -----------------------

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "database": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "port": st.secrets["DB_PORT"]
}


@st.cache_data(ttl=600)
def load_analysis():
    conn = psycopg2.connect(**DB_CONFIG)

    query = """
    SELECT
        created_at,
        summary,
        affected_assets
    FROM analysis
    ORDER BY created_at DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


df = load_analysis()

st.title("📊 AI Market Intelligence Dashboard")

if df.empty:
    st.warning("Analysis tablosunda veri yok.")
    st.stop()

# -----------------------
# JSON PARSE
# -----------------------

rows = []

for _, row in df.iterrows():
    created = pd.to_datetime(row["created_at"])

    if isinstance(row["affected_assets"], list):
        for asset in row["affected_assets"]:

            rows.append({
                "date": created,
                "asset": asset.get("asset"),
                "type": asset.get("asset_type"),
                "sentiment": asset.get("sentiment"),
                "impact_score": float(asset.get("impact_score", 0))
            })

assets_df = pd.DataFrame(rows)

if assets_df.empty:
    st.warning("Asset verisi yok.")
    st.stop()

# -----------------------
# SENTIMENT NUMERIC SCORE
# -----------------------

sentiment_map = {
    "positive": 1,
    "neutral": 0,
    "negative": -1
}

assets_df["sentiment_score"] = assets_df["sentiment"].map(sentiment_map)

assets_df["risk_score"] = (
    assets_df["sentiment_score"] * assets_df["impact_score"]
)

# -----------------------
# 1️⃣ VARLIK ETKİ SKORU
# -----------------------

st.subheader("📊 Asset Impact Scores")

asset_scores = (
    assets_df.groupby("asset")["impact_score"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig_asset = px.bar(
    asset_scores,
    x="asset",
    y="impact_score"
)

st.plotly_chart(fig_asset, use_container_width=True)

# -----------------------
# 2️⃣ SENTIMENT HEATMAP
# -----------------------

st.subheader("🔥 Sentiment Heatmap")

heatmap_df = (
    assets_df.groupby(["asset", "sentiment"])
    .size()
    .unstack(fill_value=0)
)

fig_heat = px.imshow(heatmap_df)

st.plotly_chart(fig_heat, use_container_width=True)

# -----------------------
# 3️⃣ GLOBAL SENTIMENT SCORE
# -----------------------

st.subheader("🌍 Sentiment Weighted Global Score")

global_score = assets_df["risk_score"].mean()

st.metric("Global Score", round(global_score, 3))

# -----------------------
# 4️⃣ EMA RISK GAUGE
# -----------------------

st.subheader("⚠️ Global Risk Gauge (EMA)")

daily_risk = (
    assets_df.groupby("date")["risk_score"]
    .mean()
    .sort_index()
)

ema_risk = daily_risk.ewm(span=3, adjust=False).mean()

current_risk = ema_risk.iloc[-1]

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current_risk,
    title={"text": "Market Risk EMA"},
    gauge={
        "axis": {"range": [-1, 1]},
        "steps": [
            {"range": [-1, -0.3]},
            {"range": [-0.3, 0.3]},
            {"range": [0.3, 1]}
        ]
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

# Risk label
def risk_label(score):
    if score > 0.3:
        return "🟢 Risk On"
    elif score < -0.3:
        return "🔴 Risk Off"
    return "🟡 Neutral"

st.markdown(f"### Current Market Regime: {risk_label(current_risk)}")

# -----------------------
# 5️⃣ EMA TREND GRAPH
# -----------------------

st.subheader("📈 Risk Trend (EMA Only)")

ema_df = pd.DataFrame({
    "EMA Risk": ema_risk
})

st.line_chart(ema_df)

# -----------------------
# 6️⃣ SON AI RAPORLARI
# -----------------------

st.subheader("🧠 Latest AI Reports")

for _, row in df.head(5).iterrows():
    with st.expander(str(row["created_at"])):
        st.write(row["summary"])
