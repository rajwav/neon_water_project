import pandas as pd
import joblib
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler



# ==========================
# LOAD DATA
# ==========================

print("📥 Loading dataset...")


df = pd.read_csv(
    "results/final_water_quality_prediction.csv"
)



# ==========================
# FEATURES
# ==========================

features = [

    "pH",
    "dissolvedOxygen",
    "turbidity",
    "specificConductance",
    "chlorophyll",
    "fDOM"

]


X = df[features].copy()



# ==========================
# HANDLE MISSING VALUES
# ==========================

print("🧹 Handling missing values...")


X = X.fillna(
    X.median()
)



# ==========================
# NORMALIZATION
# ==========================

print("⚖️ Scaling features...")


scaler = StandardScaler()


X_scaled = pd.DataFrame(

    scaler.fit_transform(X),

    columns=features

)



# ==========================
# TRAIN ANOMALY MODEL
# ==========================

print("🤖 Training Isolation Forest...")


model = IsolationForest(

    n_estimators=200,

    contamination=0.01,

    random_state=42,

    n_jobs=-1

)



model.fit(
    X_scaled
)



print(
    "✅ Training completed"
)



# ==========================
# PREDICTION
# ==========================

print(
    "🔍 Detecting anomalies..."
)


predictions = model.predict(
    X_scaled
)



# Isolation Forest:
# -1 = anomaly
#  1 = normal


df["predicted_anomaly"] = predictions



# ==========================
# ANOMALY SCORE
# ==========================

df["anomaly_score"] = model.decision_function(
    X_scaled
)



# ==========================
# DISTRIBUTION
# ==========================


print(
    "\nAnomaly Distribution"
)


print(
    df["predicted_anomaly"].value_counts()
)



# ==========================
# ANOMALY PERCENTAGE
# ==========================


anomaly_count = len(

    df[
        df["predicted_anomaly"] == -1
    ]

)


total_samples = len(df)



anomaly_percentage = (

    anomaly_count / total_samples

) * 100



print(

    f"Anomaly Percentage: {anomaly_percentage:.2f}%"

)



# ==========================
# COMPARE WITH RISK LABELS
# ==========================


if "final_status" in df.columns:


    print(
        "\nAI Anomaly vs Risk Status"
    )


    df["ai_anomaly"] = (

        df["predicted_anomaly"] == -1

    )


    print(

        pd.crosstab(

            df["final_status"],

            df["ai_anomaly"]

        )

    )



# ==========================
# SAVE MODEL
# ==========================


print(
    "💾 Saving model..."
)



os.makedirs(

    "models/saved_models",

    exist_ok=True

)



joblib.dump(

    model,

    "models/saved_models/anomaly_model.pkl"

)



joblib.dump(

    scaler,

    "models/saved_models/anomaly_scaler.pkl"

)



joblib.dump(

    features,

    "models/saved_models/anomaly_features.pkl"

)



print(
    "✅ Anomaly Detection Model Saved Successfully"
)


print(
    "Model:"
)

print(
    "models/saved_models/anomaly_model.pkl"
)