import pandas as pd

from src.data_loader import load_all_data


def generate_features(df):
    """
    Generate ML features from the cleaned dataset.
    """

    df = df.copy()

    # --------------------------
    # Date Features
    # --------------------------
    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.weekday
    df["quarter"] = df["date"].dt.quarter

    # --------------------------
    # ROAS
    # --------------------------
    df["roas"] = (
        df["revenue"] /
        df["spend"].replace(0, 1)
    )

    # --------------------------
    # CTR
    # --------------------------
    df["ctr"] = (
        df["clicks"] /
        df["impressions"].replace(0, 1)
    )

    # --------------------------
    # CPC
    # --------------------------
    df["cpc"] = (
        df["spend"] /
        df["clicks"].replace(0, 1)
    )

    # --------------------------
    # CPM
    # --------------------------
    df["cpm"] = (
        df["spend"] /
        df["impressions"].replace(0, 1)
    ) * 1000

    # --------------------------
    # Revenue Per Click
    # --------------------------
    df["revenue_per_click"] = (
        df["revenue"] /
        df["clicks"].replace(0, 1)
    )

    # --------------------------
    # Conversion Rate
    # --------------------------
    df["conversion_rate"] = (
        df["conversions"] /
        df["clicks"].replace(0, 1)
    )

    # Replace infinities
    df.replace(
        [float("inf"), float("-inf")],
        0,
        inplace=True
    )

    df.fillna(0, inplace=True)

    # Save processed dataset
    df.to_csv(
        "data/processed_data.csv",
        index=False
    )

    return df


if __name__ == "__main__":

    data = load_all_data()

    processed = generate_features(data)

    print("Processed Shape:", processed.shape)
    print("Processed Dataset Saved!")

    print("\nColumns:")
    print(processed.columns.tolist())

    print("\nPreview:")
    print(processed.head())