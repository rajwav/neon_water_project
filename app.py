from dashboard.components.cards import metric_card
from dashboard.components.alerts import water_alert

from dashboard.charts.sensor_charts import sensor_line_chart, anomaly_chart
from dashboard.charts.risk_charts import risk_distribution

import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Water Quality Monitoring",
    page_icon="🌊",
    layout="wide"
)


# ==========================
# LOAD DATA
# ==========================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "results/final_water_quality_prediction.csv"
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    return df


df = load_data()



# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("🔎 Monitoring Controls")


selected_site = st.sidebar.selectbox(
    "Select Monitoring Site",
    ["All"] + sorted(df["site"].unique())
)


if selected_site != "All":

    df = df[
        df["site"] == selected_site
    ]



# ==========================
# TITLE
# ==========================

st.title(
    "🌊 AI Water Quality Monitoring System"
)


st.caption(
    "Machine Learning based anomaly detection and water risk assessment"
)



# ==========================
# METRICS
# ==========================


total_samples = len(df)


total_anomalies = len(
    df[df["anomaly_status"] == -1]
)


critical_events = len(
    df[df["final_status"] == "CRITICAL"]
)


safe_events = len(
    df[df["final_status"] == "SAFE"]
)



c1,c2,c3,c4 = st.columns(4)


c1.metric(
    "Total Samples",
    f"{total_samples:,}"
)


c2.metric(
    "AI Anomalies",
    f"{total_anomalies:,}"
)


c3.metric(
    "Critical Events",
    f"{critical_events:,}"
)


c4.metric(
    "Safe Samples",
    f"{safe_events:,}"
)



st.divider()



# ==========================
# CURRENT STATUS
# ==========================


st.subheader(
    "🚦 Current Water Status"
)


latest = df.iloc[-1]


status = latest["final_status"]



if status == "SAFE":

    st.success(
        "🟢 WATER QUALITY STATUS : SAFE"
    )


elif status == "WARNING":

    st.warning(
        "🟡 WATER QUALITY STATUS : WARNING"
    )


else:

    st.error(
        "🔴 WATER QUALITY STATUS : CRITICAL"
    )



c1,c2,c3,c4 = st.columns(4)


c1.metric(
    "pH",
    round(latest["pH"],2)
)


c2.metric(
    "Dissolved Oxygen",
    round(latest["dissolvedOxygen"],2)
)


c3.metric(
    "Turbidity",
    round(latest["turbidity"],2)
)


c4.metric(
    "Risk Score",
    round(latest["final_risk_score"],2)
)



st.divider()



# ==========================
# PREPARE PLOT DATA
# ==========================


plot_data = (
    df
    .sample(min(8000,len(df)))
    .sort_values("timestamp")
)



# ==========================
# PH TREND
# ==========================


st.subheader(
    "📈 pH Variation Over Time"
)


ph_fig = px.line(
    plot_data,
    x="timestamp",
    y="pH",
    title="Water pH Trend"
)


ph_fig.update_layout(
    height=450
)


st.plotly_chart(
    ph_fig,
    use_container_width=True,
    key="ph_chart"
)



# ==========================
# SENSOR MONITORING
# ==========================


st.subheader(
    "🧪 Sensor Monitoring"
)


tab1,tab2,tab3,tab4 = st.tabs(
    [
        "Dissolved Oxygen",
        "Turbidity",
        "Conductivity",
        "Chlorophyll"
    ]
)



with tab1:

    fig_do = px.line(
        plot_data,
        x="timestamp",
        y="dissolvedOxygen",
        title="Dissolved Oxygen"
    )

    st.plotly_chart(
        fig_do,
        use_container_width=True,
        key="do_chart"
    )



with tab2:

    fig_turb = px.line(
        plot_data,
        x="timestamp",
        y="turbidity",
        title="Turbidity"
    )


    st.plotly_chart(
        fig_turb,
        use_container_width=True,
        key="turb_chart"
    )



with tab3:

    fig_cond = px.line(
        plot_data,
        x="timestamp",
        y="specificConductance",
        title="Specific Conductance"
    )


    st.plotly_chart(
        fig_cond,
        use_container_width=True,
        key="cond_chart"
    )



with tab4:

    fig_chl = px.line(
        plot_data,
        x="timestamp",
        y="chlorophyll",
        title="Chlorophyll"
    )


    st.plotly_chart(
        fig_chl,
        use_container_width=True,
        key="chl_chart"
    )



st.divider()



# ==========================
# AI ANOMALY DETECTION
# ==========================


st.subheader(
    "🤖 AI Anomaly Detection"
)



anomaly_plot = (
    df
    .sample(min(8000,len(df)))
)



anomaly_fig = px.scatter(
    anomaly_plot,
    x="timestamp",
    y="pH",
    color="anomaly_status",
    title="Detected Water Quality Anomalies"
)



st.plotly_chart(
    anomaly_fig,
    use_container_width=True,
    key="anomaly_chart"
)



# anomaly table

st.subheader(
    "⚠️ Latest Anomaly Events"
)



anomalies = (
    df[df["anomaly_status"]==-1]
    .sort_values(
        "timestamp",
        ascending=False
    )
)



st.dataframe(
    anomalies[
        [
        "timestamp",
        "site",
        "pH",
        "turbidity",
        "dissolvedOxygen",
        "final_risk_score",
        "final_status"
        ]
    ].head(50),

    use_container_width=True
)



st.divider()



# ==========================
# RISK ANALYSIS
# ==========================


st.subheader(
    "📊 Risk Distribution"
)



risk_counts = (
    df["final_status"]
    .value_counts()
)



risk_fig = px.bar(
    risk_counts,
    x=risk_counts.index,
    y=risk_counts.values,
    labels={
        "x":"Status",
        "y":"Count"
    },
    title="Water Risk Classification"
)



st.plotly_chart(
    risk_fig,
    use_container_width=True,
    key="risk_chart"
)



# ==========================
# SITE ANALYSIS
# ==========================


st.subheader(
    "📍 Site Risk Analysis"
)


site_risk = (
    df.groupby("site")
    ["final_risk_score"]
    .mean()
    .reset_index()
)



site_fig = px.bar(
    site_risk,
    x="site",
    y="final_risk_score",
    title="Average Risk Score By Site"
)



st.plotly_chart(
    site_fig,
    use_container_width=True,
    key="site_chart"
)



# ==========================
# EXPORT
# ==========================


st.divider()


st.subheader(
    "📥 Export Report"
)



csv = df.to_csv(
    index=False
)



st.download_button(
    label="Download Water Quality Report",
    data=csv,
    file_name="water_quality_report.csv",
    mime="text/csv"
)