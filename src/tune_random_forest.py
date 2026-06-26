import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score

# =====================================
# Load Data
# =====================================
data = pd.read_csv("data/processed_data.csv")

# =====================================
# Encode Campaign
# =====================================
encoder = LabelEncoder()
data["campaign_encoded"] = encoder.fit_transform(data["campaign_name"])

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
# Parameter Grid
# =====================================
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2]
}

# =====================================
# Grid Search
# =====================================
grid = GridSearchCV(
    RandomForestRegressor(random_state=42),
    param_grid,
    cv=3,
    scoring="r2",
    n_jobs=-1
)

grid.fit(X_train, y_train)

# =====================================
# Best Model
# =====================================
best_model = grid.best_estimator_

predictions = best_model.predict(X_test)

score = r2_score(y_test, predictions)

print("Best Parameters:")
print(grid.best_params_)

print()

print("Best R2 Score:", score)