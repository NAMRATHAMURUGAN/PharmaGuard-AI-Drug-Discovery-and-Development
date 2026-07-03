import numpy as np
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from sklearn.utils.class_weight import compute_sample_weight

from xgboost import XGBClassifier

print("=" * 60)
print("DDI XGBOOST TRAINING")
print("=" * 60)

# =====================================================
# LOAD DATA
# =====================================================

X = np.load("datasets/ddi_features.npy")
y = np.load("datasets/ddi_labels.npy")

print(f"\nX Shape: {X.shape}")
print(f"y Shape: {y.shape}")

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain Shape:", X_train.shape)
print("Test Shape :", X_test.shape)

# =====================================================
# HANDLE CLASS IMBALANCE
# =====================================================

sample_weights = compute_sample_weight(
    class_weight="balanced",
    y=y_train
)

# =====================================================
# XGBOOST MODEL
# =====================================================

xgb = XGBClassifier(
    objective="multi:softmax",
    num_class=3,

    n_estimators=300,

    max_depth=8,

    learning_rate=0.05,

    subsample=0.8,

    colsample_bytree=0.8,

    random_state=42,

    tree_method="hist",

    n_jobs=-1
)

print("\nTraining XGBoost...")

xgb.fit(
    X_train,
    y_train,
    sample_weight=sample_weights
)

# =====================================================
# PREDICTIONS
# =====================================================

y_pred = xgb.predict(X_test)

# =====================================================
# METRICS
# =====================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

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

# =====================================================
# CONFUSION MATRIX
# =====================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

pd.DataFrame(cm).to_csv(
    "results/ddi_xgb_confusion_matrix.csv",
    index=False
)

# =====================================================
# SAVE MODEL
# =====================================================

joblib.dump(
    xgb,
    "models/ddi_xgb.pkl"
)

print("\nSaved:")
print("models/ddi_xgb.pkl")

print("\n[DONE]")