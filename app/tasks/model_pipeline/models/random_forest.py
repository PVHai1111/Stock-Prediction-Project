# app/tasks/model_pipeline/models/random_forest.py
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score

def train_and_evaluate(X, y):
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,  # Hoặc None nếu muốn để cây tự quyết định
        class_weight='balanced',  # Xử lý mất cân bằng
        random_state=42
    )
    model.fit(X, y)
    y_pred = model.predict(X)
    print("=== Random Forest Evaluation ===")
    print(confusion_matrix(y, y_pred))
    print(classification_report(y, y_pred))
    print("ROC AUC:", roc_auc_score(y, y_pred))
    print("F1-macro:", f1_score(y, y_pred, average="macro"))
    return model

def save_model(model, feature_names, ticker: str):
    folder = "app/ml_models"
    os.makedirs(folder, exist_ok=True)
    joblib.dump(model, f"{folder}/{ticker}_rf.joblib")
    joblib.dump(feature_names, f"{folder}/{ticker}_rf_columns.pkl")

def load_model(ticker: str):
    folder = "app/ml_models"
    model = joblib.load(f"{folder}/{ticker}_rf.joblib")
    columns = joblib.load(f"{folder}/{ticker}_rf_columns.pkl")
    return model, columns


