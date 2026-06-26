import pandas as pd


REQUIRED_COLUMNS = [
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


def validate_data(df):

    print("\n" + "=" * 50)
    print("DATA VALIDATION REPORT")
    print("=" * 50)

    passed = True

    # Dataset empty
    if df.empty:
        print("[ERROR] Dataset is empty.")
        return False

    print(f"[OK] Total Rows : {len(df)}")

    # Required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

    if missing:
        print("[ERROR] Missing Columns:", missing)
        passed = False
    else:
        print("[OK] Required Columns Present")

    # Duplicate rows
    duplicates = df.duplicated().sum()

    if duplicates:
        print(f"[WARNING] Duplicate Rows : {duplicates}")
    else:
        print("[OK] No Duplicate Rows")

    # Missing values
    print("\nMissing Values")

    for col in REQUIRED_COLUMNS:

        count = df[col].isna().sum()

        if count:
            print(f"[WARNING] {col:<15}: {count}")

    # Negative spend
    negative_spend = (df["spend"] < 0).sum()

    if negative_spend:
        print(f"[ERROR] Negative Spend : {negative_spend}")
        passed = False
    else:
        print("[OK] Spend Values Valid")

    # Negative revenue
    negative_revenue = (df["revenue"] < 0).sum()

    if negative_revenue:
        print(f"[ERROR] Negative Revenue : {negative_revenue}")
        passed = False
    else:
        print("[OK] Revenue Values Valid")

    # Platform check
    valid_platforms = [
        "Google",
        "Meta",
        "Microsoft"
    ]

    invalid = df.loc[
        ~df["platform"].isin(valid_platforms),
        "platform"
    ].unique()

    if len(invalid):
        print("[WARNING] Unknown Platforms:", invalid)
    else:
        print("[OK] Platforms Valid")

    print("=" * 50)

    if passed:
        print("VALIDATION PASSED")
    else:
        print("VALIDATION FAILED")

    print("=" * 50)

    return passed


if __name__ == "__main__":

    from data_loader import load_all_data

    df = load_all_data()

    validate_data(df)