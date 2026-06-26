import pandas as pd

print("\nGOOGLE")
google = pd.read_csv("data/google_ads_campaign_stats.csv")
print(google.columns.tolist())

print("\nMETA")
meta = pd.read_csv("data/meta_ads_campaign_stats.csv")
print(meta.columns.tolist())

print("\nBING")
bing = pd.read_csv("data/bing_campaign_stats.csv")
print(bing.columns.tolist())