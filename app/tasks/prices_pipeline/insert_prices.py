# app/tasks/prices_pipeline/insert_prices.py
from sqlalchemy.orm import Session
from app.models.price import Price
from datetime import datetime
import pandas as pd

def clean_number(val):
    try:
        return int(str(val).replace(",", "").replace('"', '').strip())
    except:
        return 0

def insert_price_data(ticker: str, raw_data: list[list[str]], db: Session):
    for row in raw_data:
        try:
            price = Price(
                ticker=ticker,
                date=datetime.strptime(row[0], "%d/%m/%Y").date(),
                open=float(row[3]), high=float(row[4]), low=float(row[5]),
                close=float(row[6]), volume=clean_number(row[8]), trade_value=clean_number(row[9])
            )
            db.add(price)
        except Exception as e:
            print(f"⚠️ Bỏ qua dòng lỗi: {e}")
    db.commit()
