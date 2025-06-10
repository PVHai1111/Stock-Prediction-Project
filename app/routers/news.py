# app/routers/news.py

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from sqlalchemy import desc, or_, func
from app.db import SessionLocal
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping

router = APIRouter(prefix="/api", tags=["News"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/news")
def get_news(
    ticker: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    keyword: Optional[str] = Query(None),
    limit: int = Query(10, gt=0, le=100),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    query = db.query(News)

    # ✅ Lọc theo ticker (nếu có)
    if ticker and ticker.strip():
        subquery = db.query(NewsTickerMapping.news_id).filter(
            NewsTickerMapping.ticker == ticker.strip().upper()
        )
        if sentiment:
            subquery = subquery.filter(NewsTickerMapping.sentiment == sentiment.lower())
        query = query.filter(News.id.in_(subquery.with_entities(NewsTickerMapping.news_id)))

    # ✅ Lọc theo sector nếu không có ticker
    elif sector and sector.strip():
        subquery = db.query(NewsSectorMapping.news_id).filter(
            NewsSectorMapping.sector == sector.strip()
        )
        if sentiment:
            subquery = subquery.filter(NewsSectorMapping.sentiment == sentiment.lower())
        query = query.filter(News.id.in_(subquery.with_entities(NewsSectorMapping.news_id)))

    # ✅ Lọc theo ngày
    if start_date:
        query = query.filter(News.published_time >= start_date)
    if end_date:
        query = query.filter(News.published_time <= end_date)

    # ✅ Lọc theo từ khóa
    if keyword:
        like_pattern = f"%{keyword.lower()}%"
        query = query.filter(
            or_(
                func.lower(News.title).like(like_pattern),
                func.lower(News.content).like(like_pattern),
            )
        )

    total = query.count()
    articles = (
        query.order_by(desc(News.published_time))
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for article in articles:
        ticker_info = [
            {
                "ticker": t.ticker,
                "sentiment": t.sentiment,
                "confidence": t.confidence
            }
            for t in article.tickers
        ]
        sector_info = [
            {
                "sector": s.sector,
                "sentiment": s.sentiment,
                "confidence": s.confidence
            }
            for s in article.sector_mappings
        ]
        results.append({
            "id": article.id,
            "title": article.title,
            "link": article.link,
            "published_time": article.published_time.isoformat() if article.published_time else None,
            "summary": article.summary,
            "sapo": article.sapo,
            "content": article.content,
            "source": article.source,
            "tickers": ticker_info,
            "sectors": sector_info
        })

    return JSONResponse(content={"results": results, "total": total})












