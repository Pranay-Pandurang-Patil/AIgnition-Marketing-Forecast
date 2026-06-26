import pandas as pd

google = pd.read_csv("data/google_ads_campaign_stats.csv")
google = google.rename(columns={
    "segments_date": "date",
    "metrics_clicks": "clicks",
    "metrics_impressions": "impressions",
    "metrics_conversions_value": "revenue",
    "metrics_cost_micros": "spend"
})
google["spend"] = google["spend"] / 1000000
google = google[["date", "clicks", "impressions", "revenue", "spend", "campaign_name"]]

meta = pd.read_csv("data/meta_ads_campaign_stats.csv")
meta = meta.rename(columns={
    "date_start": "date",
    "conversion": "revenue"
})
meta = meta[["date", "clicks", "impressions", "revenue", "spend", "campaign_name"]]

bing = pd.read_csv("data/bing_campaign_stats.csv")
bing = bing.rename(columns={
    "TimePeriod": "date",
    "Revenue": "revenue",
    "Spend": "spend",
    "Clicks": "clicks",
    "Impressions": "impressions",
    "CampaignName": "campaign_name"
})
bing = bing[["date", "clicks", "impressions", "revenue", "spend", "campaign_name"]]

all_data = pd.concat([google, meta, bing])

all_data["roas"] = all_data["revenue"] / all_data["spend"]
all_data["date"] = pd.to_datetime(all_data["date"])

all_data["month"] = all_data["date"].dt.month
all_data["weekday"] = all_data["date"].dt.weekday

print(all_data[["date","month","weekday"]].head())
print(all_data["campaign_name"].nunique())