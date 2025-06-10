# app/routers/prices.py
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import SessionLocal
from app.models.price import Price
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping
from typing import Optional
from datetime import datetime
from app.tasks.prices_pipeline.run_pipeline import run as run_price_pipeline
from app.tasks.news_pipeline.run_pipeline import run_once as run_news_pipeline
from app.services.sentiment_counter import get_sentiment_map
from fastapi.responses import StreamingResponse
import io
import csv
import json
from collections import defaultdict

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/price")
def get_prices(
    ticker: str = Query(..., min_length=1),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ticker = ticker.upper()
    query = db.query(Price).filter(Price.ticker == ticker)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Price.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date không hợp lệ")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Price.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date không hợp lệ")

    price_data = query.order_by(Price.date).all()
    sentiment_map = get_sentiment_map(ticker, db)

    results = []
    for p in price_data:
        date_str = p.date.strftime("%Y-%m-%d")
        sentiment = sentiment_map.get(date_str, {"pos": 0, "neu": 0, "neg": 0})
        results.append({
            "date": date_str,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
            "value": p.trade_value,
            "positive_articles": sentiment["pos"],
            "neutral_articles": sentiment["neu"],
            "negative_articles": sentiment["neg"]
        })
    return results


@router.get("/price/update")
def update_price_data(ticker: str = Query(..., min_length=1)):
    try:
        ticker = ticker.upper()

        print(f"📈 Cập nhật dữ liệu giá cho {ticker}...")
        run_price_pipeline(ticker)

        print(f"📰 Cập nhật dữ liệu tin tức mới nhất...")
        run_news_pipeline()

        return {"message": f"✅ Đã cập nhật giá và tin tức cho mã {ticker}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/export")
def export_price_data(
    ticker: str = Query(..., min_length=1),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ticker = ticker.upper()
    query = db.query(Price).filter(Price.ticker == ticker)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Price.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date không hợp lệ")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Price.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date không hợp lệ")

    price_data = query.order_by(Price.date).all()
    sentiment_map = get_sentiment_map(ticker, db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "open", "high", "low", "close", "volume", "value", "positive_articles", "neutral_articles", "negative_articles"])

    for p in price_data:
        date_str = p.date.strftime("%Y-%m-%d")
        s = sentiment_map.get(date_str, {"pos": 0, "neu": 0, "neg": 0})
        writer.writerow([
            date_str, p.open, p.high, p.low, p.close, p.volume, p.trade_value,
            s["pos"], s["neu"], s["neg"]
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={ticker}_price_history.csv"}
    )









