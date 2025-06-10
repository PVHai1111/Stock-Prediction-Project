# app/tasks/model_pipeline/run_prediction_pipeline.py

import sys
from app.db import SessionLocal
from app.tasks.news_pipeline.run_pipeline import run_once
from app.tasks.prices_pipeline import run_pipeline as prices_pipeline
from app.tasks.model_pipeline.prepare_features import prepare_training_data
from app.tasks.model_pipeline.train_model import train_model_for_ticker
from app.services.predictor import predict_from_latest_data

def run_prediction_pipeline(ticker: str, model_name: str):
    print("🔁 Bước 1: Cập nhật tin tức mới nhất...")
    run_once()

    print(f"\n🔁 Bước 2: Cập nhật giá mới nhất cho mã {ticker}...")
    prices_pipeline.run(ticker)

    print(f"\n🧠 Bước 3: Huấn luyện mô hình {model_name} với dữ liệu mới nhất...")
    db = SessionLocal()
    try:
        df = prepare_training_data(ticker, db)
    finally:
        db.close()

    train_model_for_ticker(ticker, df)

    print(f"\n📊 Bước 4: Dự đoán chiều hướng tiếp theo từ dữ liệu mới nhất...")
    result = predict_from_latest_data(ticker, model_name)

    print("✅ Kết quả dự đoán:")
    print(result)
    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Cách dùng đúng: python3 -m app.tasks.model_pipeline.run_prediction_pipeline <ticker> <model>")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    model_name = sys.argv[2].lower()
    run_prediction_pipeline(ticker, model_name)







