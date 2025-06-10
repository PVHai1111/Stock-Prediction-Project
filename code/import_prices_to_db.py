# code/import_prices_to_db.py

import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.price import Price

# 🔁 Khởi tạo bảng nếu chưa có (hoặc sau khi DROP)
Base.metadata.create_all(bind=engine)

# 🔢 Làm sạch số lượng có dấu phẩy/thập phân
def clean_number(value):
    if pd.isna(value):
        return 0
    return int(str(value).replace(",", "").replace('"', '').strip())

def import_csv_to_db():
    db: Session = SessionLocal()

    DATA_DIR = "data/stock_price_history_crawl"
    for file in os.listdir(DATA_DIR):
        if file.endswith("_historical_data.csv"):
            ticker = file.split("_")[0].upper()
            file_path = os.path.join(DATA_DIR, file)
            print(f"📥 Importing: {ticker} from {file}")

            df = pd.read_csv(file_path)

            for _, row in df.iterrows():
                try:
                    price = Price(
                        ticker=ticker,
                        date=datetime.strptime(row["Date"], "%d/%m/%Y").date(),
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=clean_number(row["Volume"]),
                        trade_value=clean_number(row["Value"]),
                    )
                    db.add(price)
                except Exception as e:
                    print(f"⚠️ Skip row due to error: {e}")

    db.commit()
    db.close()
    print("✅ Import hoàn tất.")

if __name__ == "__main__":
    import_csv_to_db()


