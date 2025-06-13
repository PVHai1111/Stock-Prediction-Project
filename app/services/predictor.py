# app/services/predictor.py

import pandas as pd
from collections import defaultdict
from app.db import SessionLocal
from app.tasks.model_pipeline.prepare_features import prepare_latest_features
from app.tasks.model_pipeline.models import random_forest, xgboost, lightgbm
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping


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

        # 8. Lấy danh sách bài viết mới nhất
        latest_articles = latest_data.get("latest_articles", [])
        article_ids = [a["id"] for a in latest_articles if "id" in a]

        # 9. Truy vấn cảm xúc ticker/sector cho các bài viết đó
        ticker_sentiments = db.query(NewsTickerMapping).filter(
            NewsTickerMapping.news_id.in_(article_ids)
        ).all()
        sector_sentiments = db.query(NewsSectorMapping).filter(
            NewsSectorMapping.news_id.in_(article_ids)
        ).all()

        # 10. Gom nhóm theo bài viết
        ticker_map = defaultdict(list)
        for r in ticker_sentiments:
            ticker_map[r.news_id].append({
                "ticker": r.ticker,
                "sentiment": r.sentiment,
                "confidence": float(r.confidence or 0)
            })

        sector_map = defaultdict(list)
        for r in sector_sentiments:
            sector_map[r.news_id].append({
                "sector": r.sector,
                "sentiment": r.sentiment,
                "confidence": float(r.confidence or 0)
            })

        # 11. Gộp dữ liệu vào mỗi bài viết
        for article in latest_articles:
            article["tickers"] = ticker_map.get(article["id"], [])
            article["sectors"] = sector_map.get(article["id"], [])
            article["summary"] = (
                article.get("sapo") or
                article.get("summary") or
                article.get("content", "")[:300] or
                "Không có mô tả."
            )

        # 12. Trả về kết quả đầy đủ
        return {
            "ticker": ticker,
            "model": model_name,
            "prediction": "Tăng" if y_pred == 1 else "Giảm",
            "confidence": confidence,
            "features": X.iloc[0].to_dict(),
            "feature_importance": importance,
            "latest_close": latest_data.get("latest_close"),
            "date": str(latest_data.get("date")),
            "latest_articles": latest_articles,
        }

    finally:
        db.close()















