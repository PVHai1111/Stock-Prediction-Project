# app/tasks/prices_pipeline/run_pipeline.py

from sqlalchemy.orm import Session
from datetime import date
from app.db import SessionLocal
from app.models.price import Price
from app.tasks.prices_pipeline.crawl_prices import crawl_prices_for_ticker
from app.tasks.prices_pipeline.insert_prices import insert_price_data


def get_latest_date(ticker: str, db: Session) -> date:
    latest = db.query(Price.date).filter(Price.ticker == ticker).order_by(Price.date.desc()).first()
    return latest[0] if latest else date(2000, 1, 1)


def run(ticker: str):
    db: Session = SessionLocal()

    print(f"\n🚀 Đang xử lý mã cổ phiếu: {ticker}")
    max_date = get_latest_date(ticker, db)
    print(f"📅 Dữ liệu gần nhất trong DB: {max_date}")

    new_data = crawl_prices_for_ticker(ticker, max_date)
    if not new_data:
        print("ℹ️ Không có dữ liệu mới.")
    else:
        insert_price_data(ticker, new_data, db)
        print(f"✅ Đã lưu {len(new_data)} dòng mới cho {ticker}")

    db.close()


if __name__ == "__main__":
    run("")  # test đơn lẻ, sau này gọi từ bên ngoài sẽ truyền mã cụ thể


