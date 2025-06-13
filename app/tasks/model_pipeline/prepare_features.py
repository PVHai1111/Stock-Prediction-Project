# app/tasks/model_pipeline/prepare_features.py

from sqlalchemy.orm import Session
from datetime import timedelta
import pandas as pd
from sqlalchemy import func
from app.models.price import Price
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping
import json
import os

# Load mapping ticker -> sector
SECTOR_MAP_PATH = os.path.join("data", "company_ticker_list.json")
with open(SECTOR_MAP_PATH, "r", encoding="utf-8") as f:
    TICKER_TO_SECTOR = {item["ticker"].upper(): item["sector"].strip().lower() for item in json.load(f)}

SENTIMENT_MAP = {
    'pos': 'positive',
    'neg': 'negative',
    'neu': 'neutral',
    'positive': 'positive',
    'negative': 'negative',
    'neutral': 'neutral'
}


def prepare_training_data(ticker: str, db: Session) -> pd.DataFrame:
    price_data = db.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    if len(price_data) < 5:
        raise ValueError("Không đủ dữ liệu để tạo đặc trưng")

    rows = []
    skipped = 0

    for i in range(3, len(price_data) - 1):
        window_prices = price_data[i - 3:i]
        next_day_price = price_data[i + 1]

        start_date = window_prices[0].date
        end_date = window_prices[-1].date
        sector = TICKER_TO_SECTOR.get(ticker.upper())

        # Lấy sentiment từ ticker và sector
        ticker_sentiments = db.query(
            NewsTickerMapping.sentiment,
            func.count(NewsTickerMapping.id)
        ).join(News).filter(
            NewsTickerMapping.ticker == ticker,
            News.published_time >= start_date,
            News.published_time <= end_date
        ).group_by(NewsTickerMapping.sentiment).all()

        sector_sentiments = db.query(
            NewsSectorMapping.sentiment,
            func.count(NewsSectorMapping.id)
        ).join(News).filter(
            NewsSectorMapping.sector == sector,
            News.published_time >= start_date,
            News.published_time <= end_date
        ).group_by(NewsSectorMapping.sentiment).all()

        # Tổng hợp sentiment
        counts = {"positive": 0, "negative": 0}
        for sent, count in ticker_sentiments + sector_sentiments:
            mapped = SENTIMENT_MAP.get(sent.lower())
            if mapped in counts:
                counts[mapped] += count

        # Đếm bài viết duy nhất để tính total_articles và ticker_sector_ratio
        ticker_news_ids = set([
            news_id for (news_id,) in db.query(News.id).join(NewsTickerMapping).filter(
                NewsTickerMapping.ticker == ticker,
                News.published_time >= start_date,
                News.published_time <= end_date
            ).all()
        ])

        sector_news_ids = set([
            news_id for (news_id,) in db.query(News.id).join(NewsSectorMapping).filter(
                NewsSectorMapping.sector == sector,
                News.published_time >= start_date,
                News.published_time <= end_date
            ).all()
        ])

        all_news_ids = ticker_news_ids.union(sector_news_ids)
        total_articles = len(all_news_ids)
        ticker_only_count = len(ticker_news_ids)
        ticker_sector_ratio = ticker_only_count / total_articles if total_articles > 0 else 0

        # Tính phần trăm thay đổi giá
        price_change = (next_day_price.close - price_data[i].close) / price_data[i].close * 100

        # Gán nhãn (bỏ đi nhãn đi ngang)
        if -0.1 < price_change < 0.1:
            skipped += 1
            continue
        label = 1 if price_change >= 0.1 else 0

        rows.append({
            "date": price_data[i].date,
            "ticker": ticker,
            "positive": counts["positive"],
            "negative": counts["negative"],
            "total_articles": total_articles,
            "ticker_sector_ratio": ticker_sector_ratio,
            "label": label
        })

    print(f"⚠️ Đã loại bỏ {skipped} dòng đi ngang (|pct_change| < 0.1%)")
    return pd.DataFrame(rows)



def prepare_latest_features(ticker: str, db: Session) -> dict:
    prices = db.query(Price).filter(Price.ticker == ticker).order_by(Price.date.desc()).limit(4).all()
    if len(prices) < 4:
        return {}

    prices = list(reversed(prices))
    start_date = prices[0].date
    end_date = prices[-1].date
    sector = TICKER_TO_SECTOR.get(ticker.upper())

    # Truy vấn các bài viết liên quan đến ticker
    ticker_articles = (
        db.query(News)
        .join(NewsTickerMapping, News.id == NewsTickerMapping.news_id)
        .filter(
            NewsTickerMapping.ticker == ticker,
            News.published_time >= start_date,
            News.published_time <= end_date
        )
        .all()
    )

    # Truy vấn các bài viết liên quan đến sector
    sector_articles = (
        db.query(News)
        .join(NewsSectorMapping, News.id == NewsSectorMapping.news_id)
        .filter(
            NewsSectorMapping.sector == sector,
            News.published_time >= start_date,
            News.published_time <= end_date
        )
        .all()
    )

    # Loại trùng bài viết để hiển thị
    article_dict = {}
    for a in ticker_articles + sector_articles:
        article_dict[a.id] = {
            "id": a.id,
            "title": a.title,
            "published_time": a.published_time.isoformat() if a.published_time else "",
            "link": a.link,
            "sapo": a.sapo,
            "summary": a.summary,
        }

    # Đếm sentiment
    sentiment_counts = {"positive": 0, "negative": 0}
    ticker_sentiments = db.query(NewsTickerMapping.sentiment, NewsTickerMapping.news_id).join(News).filter(
        NewsTickerMapping.ticker == ticker,
        News.published_time >= start_date,
        News.published_time <= end_date
    ).all()
    sector_sentiments = db.query(NewsSectorMapping.sentiment, NewsSectorMapping.news_id).join(News).filter(
        NewsSectorMapping.sector == sector,
        News.published_time >= start_date,
        News.published_time <= end_date
    ).all()

    # Tính sentiment
    for sent, _ in ticker_sentiments + sector_sentiments:
        mapped = SENTIMENT_MAP.get(sent.lower())
        if mapped in sentiment_counts:
            sentiment_counts[mapped] += 1

    # Đếm số bài duy nhất
    ticker_news_ids = set([news_id for _, news_id in ticker_sentiments])
    sector_news_ids = set([news_id for _, news_id in sector_sentiments])
    all_article_ids = ticker_news_ids.union(sector_news_ids)

    total_articles = len(all_article_ids)
    ticker_only_count = len(ticker_news_ids)
    ticker_sector_ratio = ticker_only_count / total_articles if total_articles > 0 else 0

    return {
        "features": {
            "positive": sentiment_counts["positive"],
            "negative": sentiment_counts["negative"],
            "total_articles": total_articles,
            "ticker_sector_ratio": ticker_sector_ratio
        },
        "latest_close": prices[-1].close,
        "date": prices[-1].date,
        "latest_articles": list(article_dict.values())
    }


