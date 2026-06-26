import os
import pandas as pd

from src.data_loader import load_all_data
from src.validate_data import validate_data
from src.generate_features import generate_features
from src.forecast import generate_forecast

def main():

    print("=" * 60)
    print("AIgnition Forecast Pipeline")
    print("=" * 60)

    # -------------------------
    # Load Data
    # -------------------------
    data = load_all_data()

    # -------------------------
    # Validate
    # -------------------------
    if not validate_data(data):
        print("Validation Failed.")
        return

    # -------------------------
    # Feature Engineering
    # -------------------------
    processed = generate_features(data)

    processed["date"] = pd.to_datetime(
        processed["date"]
    )

    # -------------------------
    # Forecast
    # -------------------------
    forecast30 = generate_forecast(
        processed,
        google_budget=20000,
        meta_budget=4000,
        microsoft_budget=1500,
        days=30
    )

    forecast60 = generate_forecast(
        processed,
        google_budget=40000,
        meta_budget=8000,
        microsoft_budget=3000,
        days=60
    )

    forecast90 = generate_forecast(
        processed,
        google_budget=60000,
        meta_budget=12000,
        microsoft_budget=4500,
        days=90
    )

    final = pd.concat(
        [
            forecast30,
            forecast60,
            forecast90
        ],
        ignore_index=True
    )

    # -------------------------
    # Save Output
    # -------------------------
    os.makedirs("output", exist_ok=True)

    final.to_csv(
        "output/predictions.csv",
        index=False
    )

    # -------------------------
    # Forecast Report
    # -------------------------
    with open(
        "output/forecast_report.txt",
        "w"
    ) as f:

        f.write("=" * 60 + "\n")
        f.write("MEDIA REVENUE FORECAST REPORT\n")
        f.write("=" * 60 + "\n\n")

        for days in [30, 60, 90]:

            f.write(f"{days}-DAY FORECAST\n")
            f.write("-" * 40 + "\n")

            temp = final[
                final["days"] == days
            ]

            for _, row in temp.iterrows():

                f.write(
                    f"""
Platform : {row['platform']}
Budget   : ${row['budget']:.2f}

Revenue
P10 : ${row['revenue_p10']:.2f}
P50 : ${row['revenue_p50']:.2f}
P90 : ${row['revenue_p90']:.2f}

ROAS : {row['predicted_roas']:.2f}

Contribution : {row['contribution']:.2f} %

----------------------------------------

"""
                )

    print("\nPredictions Saved:")
    print("output/predictions.csv")

    print("\nForecast Report Saved:")
    print("output/forecast_report.txt")

    print("\nPipeline Complete")


if __name__ == "__main__":
    main()