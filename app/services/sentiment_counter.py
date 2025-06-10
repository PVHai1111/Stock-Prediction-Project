# app/services/sentiment_counter.py

import json
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping
from pathlib import Path


# ✅ Load JSON và tạo dict mapping từ ticker -> sector
def load_ticker_sector_map() -> dict[str, str]:
    json_path = Path(__file__).resolve().parents[2] / "data" / "company_ticker_list.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        entry["ticker"].upper(): entry["sector"]
        for entry in data
        if "ticker" in entry and "sector" in entry
    }


# ✅ Khởi tạo mapping 1 lần
ticker_sector_map = load_ticker_sector_map()


# ✅ Lấy danh sách sector của 1 ticker (dạng list)
def get_sector_list(ticker: str) -> list[str]:
    sector = ticker_sector_map.get(ticker.upper())
    return [sector] if sector else []


# ✅ Tính số bài viết sentiment theo ngày (từ ticker + sector)
def get_sentiment_map(ticker: str, db: Session) -> dict:
    sectors = get_sector_list(ticker)
    sentiment_map = defaultdict(lambda: {"pos": 0, "neu": 0, "neg": 0})

    # Bài viết gán trực tiếp theo ticker
    ticker_rows = (
        db.query(
            func.date(News.published_time).label("news_date"),
            NewsTickerMapping.sentiment,
            func.count().label("count")
        )
        .join(News, News.id == NewsTickerMapping.news_id)
        .filter(NewsTickerMapping.ticker == ticker.upper())
        .group_by("news_date", NewsTickerMapping.sentiment)
        .all()
    )

    # Bài viết gán theo sector
    if sectors:
        sector_rows = (
            db.query(
                func.date(News.published_time).label("news_date"),
                NewsSectorMapping.sentiment,
                func.count().label("count")
            )
            .join(News, News.id == NewsSectorMapping.news_id)
            .filter(NewsSectorMapping.sector.in_(sectors))
            .group_by("news_date", NewsSectorMapping.sentiment)
            .all()
        )
        for row in sector_rows:
            date_str = row.news_date.strftime("%Y-%m-%d")
            sentiment_map[date_str][row.sentiment] += row.count

    # Gộp kết quả từ ticker
    for row in ticker_rows:
        date_str = row.news_date.strftime("%Y-%m-%d")
        sentiment_map[date_str][row.sentiment] += row.count

    return sentiment_map

