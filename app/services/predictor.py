# app/services/predictor.py

import pandas as pd
from app.db import SessionLocal
from app.tasks.model_pipeline.prepare_features import prepare_latest_features
from app.tasks.model_pipeline.models import random_forest, xgboost, lightgbm

def predict_from_latest_data(ticker: str, model_name: str = "random_forest"):
    db = SessionLocal()
    try:
        # 1. Lấy đặc trưng mới nhất
        latest_data = prepare_latest_features(ticker, db)
        features = latest_data.get("features")

        if features is None or not isinstance(features, dict):
            raise ValueError("Không đủ dữ liệu để dự đoán.")

        # 2. Tạo DataFrame từ dict
        X = pd.DataFrame([features])

        # 3. Chọn mô hình
        model_module = {
            "random_forest": random_forest,
            "xgboost": xgboost,
            "lightgbm": lightgbm
        }.get(model_name)

        if model_module is None:
            raise ValueError(f"Mô hình không hợp lệ: {model_name}")

        # 4. Load model và thứ tự đặc trưng
        model, columns = model_module.load_model(ticker)

        # 5. Đảm bảo dùng đúng thứ tự và chỉ các cột đã được huấn luyện
        X = X.reindex(columns=columns)

        # 6. Dự đoán nhãn và xác suất
        y_pred = model.predict(X)[0]
        if hasattr(model, "predict_proba"):
            confidence = float(model.predict_proba(X)[0][1])
        else:
            confidence = None

        # 7. Tính độ quan trọng đặc trưng nếu có
        if hasattr(model, "feature_importances_"):
            importance = {
                col: float(imp)
                for col, imp in zip(columns, model.feature_importances_)
            }
        else:
            importance = {}

        # 8. Trả về kết quả đầy đủ
        return {
            "ticker": ticker,
            "model": model_name,
            "prediction": "Tăng" if y_pred == 1 else "Giảm",
            "confidence": confidence,
            "features": X.iloc[0].to_dict(),
            "feature_importance": importance,
            "latest_close": latest_data.get("latest_close"),
            "date": str(latest_data.get("date")),
            "latest_articles": latest_data.get("latest_articles", []),
        }

    finally:
        db.close()














