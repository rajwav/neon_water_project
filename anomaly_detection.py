import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("neon_clean.csv")

features = [
    "specificConductance",
    "dissolvedOxygen",
    "pH",
    "chlorophyll",
    "turbidity",
    "fDOM"
]

X = df[features]

model = IsolationForest(
    contamination=0.01,
    random_state=42
)

df["anomaly"] = model.fit_predict(X)

print(df["anomaly"].value_counts())

df.to_csv("neon_anomaly_results.csv", index=False)

print("Done")

