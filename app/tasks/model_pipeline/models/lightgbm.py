# app/tasks/model_pipeline/models/lightgbm.py

import joblib
import os
import warnings
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score

def train_and_evaluate(X, y):
    # Suppress LightGBM warnings
    warnings.filterwarnings("ignore")

    # Khởi tạo mô hình với hyperparameters được tinh chỉnh cho dữ liệu nhỏ
    model = LGBMClassifier(
        n_estimators=100,
        num_leaves=7,                # nhỏ hơn để tránh overfitting
        min_child_samples=10,        # giảm để phù hợp dữ liệu nhỏ
        min_split_gain=0,            # tránh split bị chặn bởi ngưỡng mặc định
        random_state=42,
        verbose=-1,                  # tắt cảnh báo trong stdout
        force_col_wise=True          # xử lý cột tối ưu
    )

    model.fit(X, y)
    y_pred = model.predict(X)

    print("=== LightGBM Evaluation ===")
    print(confusion_matrix(y, y_pred))
    print(classification_report(y, y_pred))
    print("ROC AUC:", roc_auc_score(y, y_pred))
    print("F1-macro:", f1_score(y, y_pred, average="macro"))
    return model

def save_model(model, feature_names, ticker: str):
    folder = "app/ml_models"
    os.makedirs(folder, exist_ok=True)
    joblib.dump(model, f"{folder}/{ticker}_lgbm.joblib")
    joblib.dump(feature_names, f"{folder}/{ticker}_lgbm_columns.pkl")

def load_model(ticker: str):
    folder = "app/ml_models"
    model = joblib.load(f"{folder}/{ticker}_lgbm.joblib")
    columns = joblib.load(f"{folder}/{ticker}_lgbm_columns.pkl")
    return model, columns





