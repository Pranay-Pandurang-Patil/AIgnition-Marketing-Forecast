import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_all_data
from src.generate_features import generate_features
from src.validate_data import validate_data
from src.forecast import generate_forecast
from src.ai_assistant import generate_ai_analysis

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AIgnition",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {
    "forecast": None,
    "total_budget": 0.0,
    "total_revenue": 0.0,
    "blended_roas": 0.0,
    "scenario": "Baseline",
    "days": 30,
    "uploaded": False,
    "last_inputs": None
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# HEADER
# ==========================================================

st.title("📈 AIgnition Marketing Forecast")

st.caption(
    "Forecast Revenue & ROAS using historical Google, Meta and Microsoft Ads data."
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("Historical Campaign Data")

    google_file = st.file_uploader(
        "Google Ads CSV",
        type="csv"
    )

    meta_file = st.file_uploader(
        "Meta Ads CSV",
        type="csv"
    )

    microsoft_file = st.file_uploader(
        "Microsoft Ads CSV",
        type="csv"
    )

    st.divider()

    st.header("Forecast Settings")

    scenario = st.selectbox(
        "Scenario",
        [
            "Baseline",
            "Growth",
            "Aggressive"
        ],
        index=0
    )

    days = st.selectbox(
        "Forecast Horizon",
        [30, 60, 90],
        index=0
    )

    google_budget = st.number_input(
        "Google Budget",
        min_value=0.0,
        value=20000.0,
        step=1000.0
    )

    meta_budget = st.number_input(
        "Meta Budget",
        min_value=0.0,
        value=4000.0,
        step=500.0
    )

    microsoft_budget = st.number_input(
        "Microsoft Budget",
        min_value=0.0,
        value=1500.0,
        step=500.0
    )

    st.divider()

    ready = all([
        google_file is not None,
        meta_file is not None,
        microsoft_file is not None
    ])
    # ======================================================
    # Detect Input Changes
    # ======================================================

    current_inputs = (
    scenario,
    days,
    google_budget,
    meta_budget,
    microsoft_budget
    )
 
    inputs_changed = (
    st.session_state.last_inputs is not None and
    current_inputs != st.session_state.last_inputs
     )
    

    generate = st.button(
        "🚀 Generate Forecast",
        disabled=not ready,
        use_container_width=True
    )

# ==========================================================
# HOME SCREEN
# ==========================================================

if not ready and st.session_state.forecast is None:

    st.info("""
### Welcome

1. Upload Google Ads CSV

2. Upload Meta Ads CSV

3. Upload Microsoft Ads CSV

4. Set Forecast Budget

5. Click **Generate Forecast**

The dashboard automatically:

- Validates data
- Generates features
- Predicts revenue
- Calculates ROAS
- Generates AI insights
- Creates downloadable reports
""")

    st.stop()
# ==========================================================
# GENERATE FORECAST
# ==========================================================

if generate:

    progress = st.progress(0)

    status = st.empty()

    # ------------------------------------------------------
    # Save Uploaded Files
    # ------------------------------------------------------

    status.info("Uploading campaign data...")

    pd.read_csv(google_file).to_csv(
        "data/google_ads_campaign_stats.csv",
        index=False
    )

    pd.read_csv(meta_file).to_csv(
        "data/meta_ads_campaign_stats.csv",
        index=False
    )

    pd.read_csv(microsoft_file).to_csv(
        "data/bing_campaign_stats.csv",
        index=False
    )

    progress.progress(15)

    # ------------------------------------------------------
    # Load Data
    # ------------------------------------------------------

    status.info("Loading campaign data...")

    data = load_all_data()

    progress.progress(30)

    # ------------------------------------------------------
    # Validate
    # ------------------------------------------------------

    status.info("Running data validation...")

    valid = validate_data(data)

    progress.progress(45)

    with st.expander(
        "Data Validation Report",
        expanded=False
    ):

        st.write(f"Rows : {len(data):,}")

        st.write(f"Duplicate Rows : {data.duplicated().sum()}")

        st.write(f"Missing Values : {data.isna().sum().sum()}")

        st.write(f"Negative Spend : {(data['spend']<0).sum()}")

        st.write(f"Negative Revenue : {(data['revenue']<0).sum()}")

        st.write(
            "Platforms :",
            sorted(data["platform"].unique())
        )

        if valid:
            st.success("Validation Passed")
        else:
            st.error("Validation Failed")

    if not valid:

        st.stop()

    progress.progress(60)

    # ------------------------------------------------------
    # Features
    # ------------------------------------------------------

    status.info("Generating features...")

    processed = generate_features(data)

    processed["date"] = pd.to_datetime(
        processed["date"]
    )

    progress.progress(75)

    # ------------------------------------------------------
    # Forecast
    # ------------------------------------------------------

    status.info("Generating forecast...")
    if (
    google_budget <= 0 and
    meta_budget <= 0 and
    microsoft_budget <= 0
    ):
      st.error(
        "At least one platform must have a budget greater than zero."
      )
      st.stop()

   
    forecast = generate_forecast(

        processed,

        google_budget,

        meta_budget,

        microsoft_budget,

        days

    )

    progress.progress(90)

    total_budget = forecast["budget"].sum()

    total_revenue = forecast["revenue_p50"].sum()

    blended_roas = (
    total_revenue / total_budget
    if total_budget > 0
    else 0
)

    # ------------------------------------------------------
    # Save Session
    # ------------------------------------------------------

    st.session_state.forecast = forecast

    st.session_state.total_budget = total_budget

    st.session_state.total_revenue = total_revenue

    st.session_state.blended_roas = blended_roas

    st.session_state.scenario = scenario

    st.session_state.days = days

    # ==========================================
    # Gemini AI Analysis
    # ==========================================

    analysis = generate_ai_analysis(
    forecast,
    scenario,
    days,
    total_budget,
    total_revenue,
    blended_roas
    )

    st.session_state.ai_analysis = analysis

    st.session_state.uploaded = True

    st.session_state.last_inputs = current_inputs

    progress.progress(100)

    status.success(
    "Forecast Generated Successfully"
    )

    st.rerun()

# ==========================================================
# LOAD LAST FORECAST
# ==========================================================

forecast = st.session_state.forecast
if inputs_changed:

    st.warning(
        "⚠ Forecast settings have changed. Click **Generate Forecast** to refresh the results."
    )

if forecast is None:

    st.stop()

total_budget = st.session_state.total_budget

total_revenue = st.session_state.total_revenue

blended_roas = st.session_state.blended_roas

scenario = st.session_state.scenario

days = st.session_state.days
# ==========================================================
# KPI CARDS
# ==========================================================

k1, k2, k3 = st.columns(3)

k1.metric(
    "Revenue",
    f"${total_revenue:,.2f}"
)

k2.metric(
    "Budget",
    f"${total_budget:,.2f}"
)

k3.metric(
    "Blended ROAS",
    f"{blended_roas:.2f}"
)


# ==========================================================
# CHARTS
# ==========================================================

left, right = st.columns(2)

with left:

    st.subheader("Revenue Forecast")

    revenue_chart = px.bar(
        forecast,
        x="platform",
        y="revenue_p50",
        color="platform",
        text="revenue_p50"
    )

    revenue_chart.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    revenue_chart.update_layout(
        showlegend=False,
        height=420
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True
    )

with right:

    st.subheader("Revenue Contribution")

    contribution_chart = px.pie(
        forecast,
        values="contribution",
        names="platform",
        hole=0.55
    )

    contribution_chart.update_layout(
        height=420
    )

    st.plotly_chart(
        contribution_chart,
        use_container_width=True
    )

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("Predicted ROAS")

    roas_chart = px.bar(
        forecast,
        x="platform",
        y="predicted_roas",
        color="platform",
        text="predicted_roas"
    )

    roas_chart.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    roas_chart.update_layout(
        showlegend=False,
        height=400
    )

    st.plotly_chart(
        roas_chart,
        use_container_width=True
    )

with right:

    st.subheader("Prediction Interval")

    interval = forecast[
        [
            "platform",
            "revenue_p10",
            "revenue_p50",
            "revenue_p90"
        ]
    ]

    interval_chart = px.bar(
        interval,
        x="platform",
        y=[
            "revenue_p10",
            "revenue_p50",
            "revenue_p90"
        ],
        barmode="group"
    )

    interval_chart.update_layout(
        height=400
    )

    st.plotly_chart(
        interval_chart,
        use_container_width=True
    )

st.divider()

# ==========================================================
# FORECAST TABLE
# ==========================================================

st.subheader("Forecast Details")

table = forecast.copy().round(2)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)
st.divider()


# ==========================================================
# AI INSIGHTS
# ==========================================================

st.divider()

st.subheader("🤖 AI Insights")

highest_revenue = forecast.loc[
    forecast["revenue_p50"].idxmax()
]

highest_roas = forecast.loc[
    forecast["predicted_roas"].idxmax()
]

lowest_roas = forecast.loc[
    forecast["predicted_roas"].idxmin()
]
# ==========================================================
# EXECUTIVE DASHBOARD
# ==========================================================

health_score = 100

if blended_roas < 2:
    health_score -= 25

if highest_revenue["contribution"] > 70:
    health_score -= 15

if lowest_roas["predicted_roas"] < 1:
    health_score -= 20

health_score = max(0, health_score)

st.subheader("📋 Executive Business Dashboard")

c1, c2 = st.columns(2)

with c1:

    if health_score >= 85:
        st.success(f"Business Health Score : {health_score}/100")

    elif health_score >= 70:
        st.info(f"Business Health Score : {health_score}/100")

    else:
        st.error(f"Business Health Score : {health_score}/100")

with c2:

    if blended_roas >= 3:
        outlook = "Excellent Growth Outlook"

    elif blended_roas >= 2:
        outlook = "Stable Growth Outlook"

    else:
        outlook = "Growth Needs Attention"

    st.metric(
        "Forecast Outlook",
        outlook
    )

st.divider()

i1, i2, i3 = st.columns(3)

i1.success(
    f"""
🏆 Highest Revenue

**{highest_revenue['platform']}**

${highest_revenue['revenue_p50']:,.2f}
"""
)

i2.info(
    f"""
📈 Best ROAS

**{highest_roas['platform']}**

{highest_roas['predicted_roas']:.2f}
"""
)

i3.warning(
    f"""
⚠ Lowest ROAS

**{lowest_roas['platform']}**

{lowest_roas['predicted_roas']:.2f}
"""
)

st.divider()



# ==========================================================
# RECOMMENDATIONS
# ==========================================================

st.subheader("💡 Recommendations")

recommendations = []

if highest_revenue["contribution"] > 70:
    recommendations.append(
        "Revenue is highly dependent on one platform. Consider diversifying budget allocation."
    )

if highest_roas["predicted_roas"] >= 3:
    recommendations.append(
        f"Increase investment in {highest_roas['platform']} campaigns."
    )

if lowest_roas["predicted_roas"] < 1:
    recommendations.append(
        f"Review or optimize {lowest_roas['platform']} campaigns before increasing spend."
    )

if len(recommendations) == 0:
    recommendations.append(
        "Current budget allocation appears balanced."
    )

for item in recommendations:
    st.write("✅", item)

st.divider()

# ==========================================================
# GEMINI AI BUSINESS ANALYSIS
# ==========================================================

st.subheader("🤖 Gemini AI Business Analysis")

if "ai_analysis" in st.session_state:

    st.markdown(
        st.session_state.ai_analysis
    )

else:

    st.info(
        "Generate a forecast to view Gemini AI analysis."
    )

st.divider()

st.divider()

# ==========================================================
# FORECAST EXPLANATION
# ==========================================================

st.subheader("📖 Forecast Explanation")

explanations = [

    "Revenue forecasts combine historical campaign performance with Machine Learning predictions.",

    "Historical ROAS is blended with model predictions to improve business realism.",

    "Budget changes directly influence expected revenue and blended ROAS.",

    "Prediction intervals (P10 / P50 / P90) represent forecast uncertainty rather than exact values.",

    "Higher budgets generally increase forecast revenue but do not always improve ROAS.",

    "Seasonality and historical campaign behaviour are incorporated through engineered features."

]

for item in explanations:

    st.write("•", item)

st.info(
    """
P10 = Conservative Forecast

P50 = Most Likely Forecast

P90 = Optimistic Forecast
"""
)

st.divider()
st.divider()

# ==========================================================
# OPERATIONAL RISK ASSESSMENT
# ==========================================================

st.subheader("⚠ Operational Risk Assessment")

risks = []

# Revenue concentration
if highest_revenue["contribution"] >= 70:
    risks.append(
        "High dependency on a single advertising platform may increase business risk."
    )

# Low ROAS
if lowest_roas["predicted_roas"] < 1:
    risks.append(
        f"{lowest_roas['platform']} is expected to generate a ROAS below 1.0."
    )

# Budget concentration
largest_budget = forecast["budget"].max()

if largest_budget >= forecast["budget"].sum() * 0.70:
    risks.append(
        "Budget allocation is heavily concentrated in one platform."
    )

# Forecast uncertainty
average_interval = (
    (
        forecast["revenue_p90"] -
        forecast["revenue_p10"]
    ).mean()
)

if average_interval > forecast["revenue_p50"].mean() * 0.30:
    risks.append(
        "Forecast uncertainty is relatively high."
    )

if len(risks) == 0:

    st.success(
        "No significant operational risks detected based on the current forecast."
    )

else:

    for risk in risks:

        st.warning(risk)

st.divider()
# ==========================================================
# MODEL SUMMARY
# ==========================================================

with st.expander("Model Summary"):

    st.markdown(f"""
### Scenario

**{scenario}**

### Forecast Horizon

**{days} Days**

### Forecast Revenue

**${total_revenue:,.2f}**

### Forecast Budget

**${total_budget:,.2f}**

### Blended ROAS

**{blended_roas:.2f}**

### Forecast Method

- Random Forest Regression
- Budget Simulation
- Prediction Intervals (P10 / P50 / P90)
- Historical Campaign Performance
""")

st.divider()

# ==========================================================
# DOWNLOADS
# ==========================================================
download_forecast = forecast.copy()
# ==========================================================
# BUSINESS SUMMARY COLUMNS
# ==========================================================

download_forecast["AI Summary"] = ""

download_forecast["Recommendation"] = ""

download_forecast["Risk Level"] = ""

download_forecast["Confidence"] = ""

download_forecast["Priority"] = ""

for idx, row in download_forecast.iterrows():

    # AI Summary
    # AI Summary

    if row["budget"] == 0:

     summary = "No forecast generated because the platform budget is zero."

    elif row["predicted_roas"] >= 3:

     summary = "Excellent ROAS with strong revenue potential."

    elif row["predicted_roas"] >= 2:

     summary = "Good performance with stable expected returns."

    elif row["predicted_roas"] >= 1:

     summary = "Moderate performance. Optimization recommended."

    else:

     summary = "Low expected return. Review campaign strategy."

    # Recommendation
    if row["budget"] == 0:
        recommendation = "No budget allocated. Forecast excluded."
    elif row["predicted_roas"] >= 3:
        recommendation = "Increase budget."
    elif row["predicted_roas"] >= 2:
        recommendation = "Maintain current budget."
    else:
        recommendation = "Optimize before increasing spend."

    # Risk Level
    if row["predicted_roas"] >= 3:
        risk = "Low"
    elif row["predicted_roas"] >= 2:
        risk = "Medium"
    else:
        risk = "High"

    # Confidence
    interval_width = row["revenue_p90"] - row["revenue_p10"]

    if interval_width < row["revenue_p50"] * 0.20:
        confidence = "High"
    elif interval_width < row["revenue_p50"] * 0.40:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Priority
    if row["budget"] == 0:
        priority = "Paused"
    elif row["predicted_roas"] >= 3:
        priority = "Scale"
    elif row["predicted_roas"] >= 2:
        priority = "Maintain"
    else:
        priority = "Optimize"

    download_forecast.at[idx, "AI Summary"] = summary
    download_forecast.at[idx, "Recommendation"] = recommendation
    download_forecast.at[idx, "Risk Level"] = risk
    download_forecast.at[idx, "Confidence"] = confidence
    download_forecast.at[idx, "Priority"] = priority
download_forecast = download_forecast.round({
    "budget": 2,
    "revenue_p10": 2,
    "revenue_p50": 2,
    "revenue_p90": 2,
    "predicted_roas": 2,
    "contribution": 2
})

download_forecast["contribution"] = (
    download_forecast["contribution"].round(2)
)
csv = download_forecast.to_csv(
    index=False
).encode("utf-8")

c1, c2 = st.columns(2)

c1.download_button(
    "📥 Download Predictions CSV",
    csv,
    file_name="predictions.csv",
    mime="text/csv",
    use_container_width=True
)

report = f"""
AIgnition AI Marketing Forecast Report
======================================

Scenario : {scenario}

Forecast Horizon : {days} Days

Generated On : {pd.Timestamp.now().strftime("%d-%b-%Y %I:%M %p")}

Forecast Revenue : ${total_revenue:,.2f}

Forecast Budget : ${total_budget:,.2f}

Platforms Analysed : {forecast['platform'].nunique()}

Blended ROAS : {blended_roas:.2f}

Highest Revenue Platform :
{highest_revenue['platform']}

Highest ROAS Platform :
{highest_roas['platform']}

Lowest ROAS Platform :
{lowest_roas['platform']}

======================================================
RULE-BASED AI INSIGHTS
======================================================

Highest Revenue Platform :
{highest_revenue['platform']}

Best ROAS Platform :
{highest_roas['platform']}

Lowest ROAS Platform :
{lowest_roas['platform']}

======================================================
GEMINI AI BUSINESS ANALYSIS
======================================================

{st.session_state.get("ai_analysis", "Gemini AI analysis unavailable.")}

======================================================
Prediction Interval Guide
======================================================

P10 : Conservative Revenue Estimate

P50 : Expected Revenue Estimate

P90 : Optimistic Revenue Estimate
"""

c2.download_button(
    "📄 Download Forecast Report",
    report,
    file_name="forecast_report.txt",
    mime="text/plain",
    use_container_width=True
)

st.caption(
    "Last Forecast: "
    + pd.Timestamp.now().strftime("%d-%m-%Y %H:%M:%S")
)