import pandas as pd
import joblib
import os

from imblearn.ensemble import BalancedRandomForestClassifier

from sklearn.preprocessing import LabelEncoder

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score
)

import matplotlib.pyplot as plt
import seaborn as sns


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


# ==========================
# LABEL ENCODING
# ==========================

encoder = LabelEncoder()


df["label"] = encoder.fit_transform(
    df["final_status"]
)


print(
    "Classes:",
    encoder.classes_
)

# ==========================
# TIME BASED SPLIT
# ==========================

print("⏳ Creating time split...")


df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)



# Training data

train_data = df[
    df["timestamp"].dt.year == 2024
]


# Testing data

test_data = df[
    df["timestamp"].dt.year == 2025
]


print(
    "Training samples:",
    len(train_data)
)


print(
    "Testing samples:",
    len(test_data)
)



X_train = train_data[features].copy()

X_test = test_data[features].copy()


y_train = train_data["label"].copy()

y_test = test_data["label"].copy()



# ==========================
# HANDLE MISSING VALUES
# ==========================

print("🧹 Handling missing values...")


median_values = X_train.median()


X_train = X_train.fillna(
    median_values
)


X_test = X_test.fillna(
    median_values
)



# ==========================
# SMOTE BALANCING
# ==========================

'''print("⚖️ Applying SMOTE...")


print("Before SMOTE:")

print(
    y_train.value_counts()
)



smote = SMOTE(
    random_state=42
)


X_train, y_train = smote.fit_resample(
    X_train,
    y_train
)



print("After SMOTE:")

print(
    pd.Series(y_train).value_counts()
)

'''

# ==========================
# TRAIN MODEL
# ==========================

print("🤖 Training Balanced Random Forest...")


model = BalancedRandomForestClassifier(

    n_estimators=200,

    random_state=42,

    n_jobs=-1

)



model.fit(
    X_train,
    y_train
)



print(
    "✅ Training completed"
)



# ==========================
# PREDICTION
# ==========================

print(
    "🔮 Prediction started..."
)


predictions = model.predict(
    X_test
)


print(
    "✅ Prediction completed"
)



# ==========================
# CONFUSION MATRIX
# ==========================


cm = confusion_matrix(
    y_test,
    predictions
)



plt.figure(
    figsize=(7,6)
)


sns.heatmap(

    cm,

    annot=True,

    fmt="d",

    xticklabels=encoder.classes_,

    yticklabels=encoder.classes_

)


plt.xlabel(
    "Predicted"
)


plt.ylabel(
    "Actual"
)


plt.title(
    "Water Risk Classification Confusion Matrix"
)



os.makedirs(
    "results",
    exist_ok=True
)


plt.savefig(
    "results/confusion_matrix.png"
)


plt.close()



print(
    "✅ Confusion matrix saved"
)



# ==========================
# CLASSIFICATION REPORT
# ==========================


report = classification_report(
    y_test,
    predictions,
    target_names=encoder.classes_,
    digits=4
)


print(report)



# ==========================
# TEST ACCURACY
# ==========================


test_accuracy = model.score(

    X_test,

    y_test

)


print(
    f"Test Accuracy: {test_accuracy:.4f}"
)



# ==========================
# ROC AUC
# ==========================


print(
    "📊 Calculating ROC-AUC..."
)


probabilities = model.predict_proba(
    X_test
)



auc = roc_auc_score(

    y_test,

    probabilities,

    multi_class="ovr"

)



print(
    f"ROC-AUC Score: {auc:.4f}"
)



# ==========================
# FEATURE IMPORTANCE
# ==========================


importance = pd.DataFrame({

    "Feature": features,

    "Importance": model.feature_importances_

})



importance = importance.sort_values(

    by="Importance",

    ascending=False

)



print(
    importance
)



plt.figure(
    figsize=(8,5)
)


sns.barplot(

    data=importance,

    x="Importance",

    y="Feature"

)



plt.title(
    "Water Quality Feature Importance"
)



plt.savefig(
    "results/feature_importance.png"
)


plt.close()



print(
    "✅ Feature importance saved"
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

    "models/saved_models/risk_model.pkl"

)



joblib.dump(

    encoder,

    "models/saved_models/status_encoder.pkl"

)



metadata = {

    "model": "Balanced Random Forest",

    "features": features,

    "training_samples": len(X_train),

    "testing_samples": len(X_test),

    "test_accuracy": float(test_accuracy),

    "roc_auc": float(auc)

}



joblib.dump(

    metadata,

    "models/saved_models/model_metadata.pkl"

)



print(
    "✅ Advanced Risk Classification Model Saved Successfully"
)


