import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

print("=" * 60)
print("DDI RANDOM FOREST TRAINING")
print("=" * 60)

# ======================================
# LOAD DATA
# ======================================

X = np.load("datasets/ddi_features.npy")
y = np.load("datasets/ddi_labels.npy")

print(f"\nX Shape: {X.shape}")
print(f"y Shape: {y.shape}")

# ======================================
# TRAIN TEST SPLIT
# ======================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain Shape:", X_train.shape)
print("Test Shape :", X_test.shape)

# ======================================
# MODEL
# ======================================

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest...")

rf.fit(X_train, y_train)

# ======================================
# PREDICTION
# ======================================

y_pred = rf.predict(X_test)

# ======================================
# METRICS
# ======================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted"
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted"
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted"
)

print("\nRESULTS")
print("-" * 40)

print("Accuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))

print("\nClassification Report\n")

print(
    classification_report(
        y_test,
        y_pred
    )
)

# ======================================
# SAVE MODEL
# ======================================

joblib.dump(
    rf,
    "models/ddi_rf.pkl"
)

print("\nSaved:")
print("models/ddi_rf.pkl")

print("\n[DONE]")