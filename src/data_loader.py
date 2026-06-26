import os
import pandas as pd


# ==========================================
# Google Ads Standardization
# ==========================================
def standardize_google(df):

    df = df.rename(columns={
        "segments_date": "date",
        "metrics_clicks": "clicks",
        "metrics_impressions": "impressions",
        "metrics_cost_micros": "spend",
        "metrics_conversions_value": "revenue",
        "metrics_conversions": "conversions",
        "campaign_advertising_channel_type": "campaign_type",
        "campaign_budget_amount": "daily_budget"
    })

    # Convert micros to currency
    df["spend"] = df["spend"] / 1_000_000

    df["platform"] = "Google"

    return df


# ==========================================
# Meta Ads Standardization
# ==========================================
def standardize_meta(df):

    df = df.rename(columns={
        "date_start": "date",
        "conversion": "conversions"
    })

    # Revenue not available
    df["revenue"] = 0

    # Campaign type not available
    df["campaign_type"] = "Meta"

    df["platform"] = "Meta"

    return df


# ==========================================
# Microsoft/Bing Standardization
# ==========================================
def standardize_bing(df):

    df = df.rename(columns={
        "TimePeriod": "date",
        "Revenue": "revenue",
        "Spend": "spend",
        "Clicks": "clicks",
        "Impressions": "impressions",
        "Conversions": "conversions",
        "CampaignType": "campaign_type",
        "CampaignName": "campaign_name",
        "DailyBudget": "daily_budget"
    })

    df["platform"] = "Microsoft"

    return df


# ==========================================
# Load and Merge All Data
# ==========================================
def load_all_data(data_dir="data"):

    frames = []

    for file in os.listdir(data_dir):

        if not file.lower().endswith(".csv"):
            continue

        filename = file.lower()

        # Ignore generated files
        if filename.startswith(("processed", "prediction", "forecast")):
            continue

        path = os.path.join(data_dir, file)

        df = pd.read_csv(path)

        # Detect platform
        if "google" in filename:

            df = standardize_google(df)

        elif "meta" in filename or "facebook" in filename:

            df = standardize_meta(df)

        elif "bing" in filename or "microsoft" in filename:

            df = standardize_bing(df)

        else:

            print(f"Skipping {file}")
            continue

        # Final common schema
        keep_columns = [
            "date",
            "platform",
            "campaign_name",
            "campaign_type",
            "clicks",
            "impressions",
            "spend",
            "revenue",
            "conversions",
            "daily_budget"
        ]

        # Create missing columns
        for col in keep_columns:
            if col not in df.columns:
                df[col] = 0

        df = df[keep_columns]

        frames.append(df)

        print(f"Loaded: {file}")

    # Merge datasets
    combined = pd.concat(
        frames,
        ignore_index=True
    )

    # Fill missing values
    combined["daily_budget"] = combined["daily_budget"].fillna(0)
    combined["conversions"] = combined["conversions"].fillna(0)
    combined["revenue"] = combined["revenue"].fillna(0)
    combined["campaign_type"] = combined["campaign_type"].fillna("Unknown")
    combined["campaign_name"] = combined["campaign_name"].fillna("Unknown")

    # Convert date
    combined["date"] = pd.to_datetime(
        combined["date"],
        errors="coerce"
    )

    print("\nTotal Rows:", len(combined))

    return combined


# ==========================================
# Test
# ==========================================
if __name__ == "__main__":

    data = load_all_data()

    print("\nColumns:")
    print(data.columns)

    print("\nFirst 5 Rows:")
    print(data.head())