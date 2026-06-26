import pandas as pd


def generate_insights(df):

    insights = []

    highest = df.loc[df["revenue_p50"].idxmax()]

    insights.append(
        f"Highest Revenue Platform : {highest['platform']}"
    )

    highest_roas = df.loc[
        df["predicted_roas"].idxmax()
    ]

    insights.append(
        f"Highest ROAS : {highest_roas['platform']}"
    )

    lowest_roas = df.loc[
        df["predicted_roas"].idxmin()
    ]

    insights.append(
        f"Lowest ROAS : {lowest_roas['platform']}"
    )

    if highest["contribution"] > 70:
        insights.append(
            "Risk : Revenue heavily depends on one platform."
        )

    insights.append(
        "Forecast Confidence : Medium (ML + Historical Patterns)"
    )

    return insights


if __name__ == "__main__":

    df = pd.read_csv("output/predictions.csv")

    for line in generate_insights(df):
        print(line)