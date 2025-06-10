# app/tasks/news_pipeline/insert_to_db.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping
from datetime import datetime

def run(articles: list[dict]):
    db: Session = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    for article in articles:
        try:
            # Check trùng link
            if db.query(News).filter(News.link == article["link"]).first():
                skipped_count += 1
                continue

            # Tạo bản ghi News
            news = News(
                title=article["title"],
                link=article["link"],
                published_time=datetime.fromisoformat(article["published_time"]),
                summary=article.get("summary"),
                price_change_info=article.get("price_change_info"),
                category=article.get("category"),
                sapo=article.get("sapo"),
                content=article.get("content"),
                source=article.get("source"),
            )
            db.add(news)
            db.flush()  # để news.id có thể dùng luôn

            # Chèn ticker mapping
            ticker_sentiments = article.get("ticker_sentiments", {})
            for ticker, senti in ticker_sentiments.items():
                mapping = NewsTickerMapping(
                    news_id=news.id,
                    ticker=ticker,
                    sentiment=senti.get("sentiment"),
                    confidence=senti.get("confidence"),
                )
                db.add(mapping)

            sector_sentiments = article.get("sector_sentiments", {})
            for sector, senti in sector_sentiments.items():
                mapping = NewsSectorMapping(
                    news_id=news.id,
                    sector=sector,
                    sentiment=senti.get("sentiment"),
                    confidence=senti.get("confidence"),
                )
                db.add(mapping)


            db.commit()
            inserted_count += 1

        except Exception as e:
            db.rollback()
            print(f"❌ Lỗi khi xử lý bài viết '{article.get('title', '')}': {e}")

    db.close()
    print(f"✅ Đã thêm {inserted_count} bài viết. Bỏ qua {skipped_count} bài trùng.")


