import pandas as pd

from src.data_loader import load_all_data

def simulate_budget(data,
                    google_budget,
                    meta_budget,
                    microsoft_budget):

    simulation = []

    budgets = {
        "Google": google_budget,
        "Meta": meta_budget,
        "Microsoft": microsoft_budget
    }

    for platform, budget in budgets.items():

        platform_data = data[
            data["platform"] == platform
        ]

        if platform_data.empty:
            continue

        avg_ctr = platform_data["ctr"].mean()
        avg_cpc = platform_data["cpc"].mean()
        avg_cpm = platform_data["cpm"].mean()
        avg_conversion = platform_data["conversion_rate"].mean()

        # Estimate clicks
        clicks = budget / max(avg_cpc, 0.01)

        # Estimate impressions
        impressions = clicks / max(avg_ctr, 0.001)

        simulation.append({

            "platform": platform,

            "budget": budget,

            "estimated_clicks": round(clicks),

            "estimated_impressions": round(impressions),

            "ctr": avg_ctr,

            "cpc": avg_cpc,

            "cpm": avg_cpm,

            "conversion_rate": avg_conversion

        })

    return pd.DataFrame(simulation)


if __name__ == "__main__":

    data = pd.read_csv("data/processed_data.csv")

    result = simulate_budget(
        data,
        google_budget=20000,
        meta_budget=4000,
        microsoft_budget=1500
    )

    print(result)