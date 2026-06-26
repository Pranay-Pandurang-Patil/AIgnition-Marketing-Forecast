import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    root_mean_squared_error
)

# ==========================================
# Load Processed Dataset
# ==========================================
data = pd.read_csv("data/processed_data.csv")

# ==========================================
# Encode Campaign Name
# ==========================================
campaign_encoder = LabelEncoder()

data["campaign_encoded"] = campaign_encoder.fit_transform(
    data["campaign_name"]
)

pickle.dump(
    campaign_encoder,
    open("pickle/campaign_encoder.pkl", "wb")
)

# ==========================================
# Encode Platform
# ==========================================
platform_encoder = LabelEncoder()

data["platform_encoded"] = platform_encoder.fit_transform(
    data["platform"]
)

pickle.dump(
    platform_encoder,
    open("pickle/platform_encoder.pkl", "wb")
)

# ==========================================
# Features (NO DATA LEAKAGE)
# ==========================================
X = data[
    [
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
    ]
]

# ==========================================
# Target
# ==========================================
y = data["revenue"]

# ==========================================
# Train/Test Split
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================
# Model
# ==========================================
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=20,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

# ==========================================
# Train
# ==========================================
model.fit(X_train, y_train)

# ==========================================
# Predict
# ==========================================
predictions = model.predict(X_test)

# ==========================================
# Evaluation
# ==========================================
r2 = r2_score(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)
rmse = root_mean_squared_error(y_test, predictions)

# ==========================================
# Save Model
# ==========================================
pickle.dump(
    model,
    open("pickle/model.pkl", "wb")
)

# ==========================================
# Results
# ==========================================
print("=" * 50)
print("MODEL TRAINING COMPLETE")
print("=" * 50)

print("Training Rows :", len(X_train))
print("Testing Rows  :", len(X_test))

print(f"\nR2 Score : {r2:.4f}")
print(f"MAE      : {mae:.4f}")
print(f"RMSE     : {rmse:.4f}")

print("\nModel Saved      : pickle/model.pkl")
print("Campaign Encoder : Saved")
print("Platform Encoder : Saved")

print("=" * 50)