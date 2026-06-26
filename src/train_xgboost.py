import pandas as pd
import pickle


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
from xgboost import XGBRegressor

# =====================================
# Load Processed Dataset
# =====================================
data = pd.read_csv("data/processed_data.csv")

# =====================================
# Encode Campaign
# =====================================
encoder = LabelEncoder()

data["campaign_encoded"] = encoder.fit_transform(
    data["campaign_name"]
)

# =====================================
# Features
# =====================================
X = data[
    [
        "clicks",
        "impressions",
        "spend",
        "month",
        "weekday",
        "campaign_encoded"
    ]
]

# =====================================
# Target
# =====================================
y = data["revenue"]

# =====================================
# Train Test Split
# =====================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# =====================================
# XGBoost Model
# =====================================
model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# =====================================
# Train
# =====================================
model.fit(X_train, y_train)

# =====================================
# Prediction
# =====================================
predictions = model.predict(X_test)

score = r2_score(y_test, predictions)

# =====================================
# Save Model
# =====================================
pickle.dump(
    model,
    open("pickle/xgboost_model.pkl", "wb")
)

# =====================================
# Results
# =====================================
print("Training Rows:", len(X_train))
print("Testing Rows:", len(X_test))
print("XGBoost R2 Score:", score)
print("XGBoost Model Saved!")