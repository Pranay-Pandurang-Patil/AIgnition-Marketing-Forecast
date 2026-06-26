import pickle
import pandas as pd

from src.budget_simulator import simulate_budget
from src.prediction_intervals import predict_interval

# ==========================================================
# Load Model & Encoders
# ==========================================================

model = pickle.load(
    open("pickle/model.pkl", "rb")
)

campaign_encoder = pickle.load(
    open("pickle/campaign_encoder.pkl", "rb")
)

platform_encoder = pickle.load(
    open("pickle/platform_encoder.pkl", "rb")
)

# ==========================================================
# Forecast Function
# ==========================================================

def generate_forecast(
    processed_data,
    google_budget,
    meta_budget,
    microsoft_budget,
    days
):

    simulation = simulate_budget(
        processed_data,
        google_budget,
        meta_budget,
        microsoft_budget
    )

    latest_date = processed_data["date"].max()

    forecasts = []

    for _, row in simulation.iterrows():

        platform = row["platform"]

        # --------------------------------------------------
        # Skip Forecast for Zero Budget Platforms
        # --------------------------------------------------

        if row["budget"] <= 0:

            forecasts.append({

                "days": days,

                "platform": platform,

                "budget": 0.0,

                "revenue_p10": 0.0,

                "revenue_p50": 0.0,

                "revenue_p90": 0.0,

                "predicted_roas": 0.0

            })

            continue

        platform_data = processed_data[
            processed_data["platform"] == platform
        ]

        if platform_data.empty:
            continue

        # --------------------------------------------------
        # Most Common Campaign
        # --------------------------------------------------

        campaign = (
            platform_data["campaign_name"]
            .mode()
            .iloc[0]
        )

        forecast_date = latest_date + pd.Timedelta(
            days=days
        )

        month = forecast_date.month
        weekday = forecast_date.weekday()
        quarter = forecast_date.quarter

        campaign_encoded = campaign_encoder.transform(
            [campaign]
        )[0]

        platform_encoded = platform_encoder.transform(
            [platform]
        )[0]

        conversions = (
            row["estimated_clicks"] *
            row["conversion_rate"]
        )

        X = pd.DataFrame([{

            "clicks": row["estimated_clicks"],

            "impressions": row["estimated_impressions"],

            "spend": row["budget"],

            "conversions": conversions,

            "daily_budget": row["budget"] / days,

            "month": month,

            "weekday": weekday,

            "quarter": quarter,

            "ctr": row["ctr"],

            "cpc": row["cpc"],

            "cpm": row["cpm"],

            "campaign_encoded": campaign_encoded,

            "platform_encoded": platform_encoded

        }])

        X = X[[
            "clicks",
            "impressions",
            "spend",
            "conversions",
            "daily_budget",
            "month",
            "weekday",
            "quarter",
            "ctr",
            "cpc",
            "cpm",
            "campaign_encoded",
            "platform_encoded"
        ]]

        # --------------------------------------------------
        # ML Prediction
        # --------------------------------------------------

        p10, p50, p90 = predict_interval(X.values)

        ml_prediction = float(p50[0])

        # --------------------------------------------------
        # Historical ROAS
        # --------------------------------------------------

        historical_spend = platform_data["spend"].sum()

        historical_revenue = platform_data["revenue"].sum()

        if historical_spend == 0:

            historical_roas = 1.0

        else:

            historical_roas = (
                historical_revenue /
                historical_spend
            )

        expected_revenue = (
            row["budget"] *
            historical_roas
        )

        # --------------------------------------------------
        # Final Revenue
        # 70% Historical + 30% ML
        # --------------------------------------------------

        revenue = (
            expected_revenue * 0.70 +
            ml_prediction * 0.30
        )

        if row["budget"] > 0:
            roas = revenue / row["budget"]
        else:
            roas = 0.0

        forecasts.append({

            "days": days,

            "platform": platform,

            "budget": round(row["budget"], 2),

            "revenue_p10": round(revenue * 0.90, 2),

            "revenue_p50": round(revenue, 2),

            "revenue_p90": round(revenue * 1.10, 2),

            "predicted_roas": round(roas, 2)

        })

    result = pd.DataFrame(forecasts)

    total = result["revenue_p50"].sum()

    if total > 0:

     result["contribution"] = (
        result["revenue_p50"] / total
    ) * 100

    else:

     result["contribution"] = 0.0

    return result


# ==========================================================
# Test
# ==========================================================
if __name__ == "__main__":

    data = pd.read_csv(
        "data/processed_data.csv"
    )

    data["date"] = pd.to_datetime(
        data["date"]
    )

    forecast30 = generate_forecast(
        data,
        20000,
        4000,
        1500,
        30
    )

    forecast60 = generate_forecast(
        data,
        40000,
        8000,
        3000,
        60
    )

    forecast90 = generate_forecast(
        data,
        60000,
        12000,
        4500,
        90
    )

    final = pd.concat(
        [
            forecast30,
            forecast60,
            forecast90
        ],
        ignore_index=True
    )

    final.to_csv(
        "output/predictions.csv",
        index=False
    )

    print("=" * 70)
    print(final)
    print("=" * 70)

    print("\nPredictions Saved!")
    