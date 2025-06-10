# app/tasks/model_pipeline/models/xgboost.py

import joblib
import os
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score

def train_and_evaluate(X, y):
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        scale_pos_weight=1.0,  # hoặc tự động tính theo tỉ lệ
        random_state=42
    )

    model.fit(X, y)
    y_pred = model.predict(X)
    print("=== XGBoost Evaluation ===")
    print(confusion_matrix(y, y_pred))
    print(classification_report(y, y_pred))
    print("ROC AUC:", roc_auc_score(y, y_pred))
    print("F1-macro:", f1_score(y, y_pred, average="macro"))
    return model

def save_model(model, feature_names, ticker: str):
    folder = "app/ml_models"
    os.makedirs(folder, exist_ok=True)
    joblib.dump(model, f"{folder}/{ticker}_xgb.joblib")
    joblib.dump(feature_names, f"{folder}/{ticker}_xgb_columns.pkl")

def load_model(ticker: str):
    folder = "app/ml_models"
    model = joblib.load(f"{folder}/{ticker}_xgb.joblib")
    columns = joblib.load(f"{folder}/{ticker}_xgb_columns.pkl")
    return model, columns

