# app/tasks/news_pipeline/run_full_annotation.py
from app.db import SessionLocal
from app.models.news import News
from app.models.news_ticker_mapping import NewsTickerMapping
from app.models.news_sector_mapping import NewsSectorMapping
from app.tasks.news_pipeline import (
    tag_tickers,
    tag_sectors,
    analyze_sentiment_per_entity,
    preprocess_articles
)
from sqlalchemy.orm import Session

def convert_news_to_dict(news_list):
    return [{
        "id": news.id,
        "title": news.title,
        "sapo": news.sapo,
        "summary": news.summary,
        "content": news.content,
        "published_time": news.published_time.isoformat() if news.published_time else "",
        "link": news.link,
        "category": news.category or "",
        "price_change_info": news.price_change_info or ""
    } for news in news_list]

def update_sentiment_to_db(articles: list[dict], db: Session):
    updated, skipped = 0, 0
    ticker_count, sector_count = 0, 0

    for article in articles:
        news_id = article.get("id")
        if not news_id:
            skipped += 1
            continue

        try:
            db.query(NewsTickerMapping).filter(NewsTickerMapping.news_id == news_id).delete()
            db.query(NewsSectorMapping).filter(NewsSectorMapping.news_id == news_id).delete()

            for ticker, senti in article.get("ticker_sentiments", {}).items():
                db.add(NewsTickerMapping(
                    news_id=news_id,
                    ticker=ticker,
                    sentiment=senti.get("sentiment"),
                    confidence=senti.get("confidence")
                ))
                ticker_count += 1

            for sector, senti in article.get("sector_sentiments", {}).items():
                db.add(NewsSectorMapping(
                    news_id=news_id,
                    sector=sector,
                    sentiment=senti.get("sentiment"),
                    confidence=senti.get("confidence")
                ))
                sector_count += 1

            updated += 1
        except Exception as e:
            db.rollback()
            print(f"❌ Lỗi khi cập nhật bài viết ID={news_id}: {e}")
            continue

    db.commit()
    print(f"✅ Đã cập nhật sentiment cho {updated} bài viết. Bỏ qua {skipped} bài lỗi.")
    print(f"🔢 Tổng số nhãn ticker: {ticker_count}, nhãn sector: {sector_count}")

def run(limit_test=30000):
    db = SessionLocal()
    try:
        news_list = db.query(News).order_by(News.published_time.desc()).limit(limit_test).all()
        print(f"📝 Tổng số bài viết lấy ra: {len(news_list)}")

        raw_articles = convert_news_to_dict(news_list)
        preprocessed_articles = preprocess_articles.run(raw_articles)

        print("🏷️ Đang gán ticker...")
        tag_tickers.run(preprocessed_articles)

        total_ticker_tags = sum(len(a.get("tickers", [])) for a in preprocessed_articles)
        ticker_by_code_count = sum(len([t for t in a.get("tickers", []) if t.get("source") == "code"]) for a in preprocessed_articles)
        ticker_by_company_count = sum(len([t for t in a.get("tickers", []) if t.get("source") == "company"]) for a in preprocessed_articles)

        print(f"🔢 Tổng số ticker được gán: {total_ticker_tags}")
        print(f"   └─ Tìm thấy qua mã ticker: {ticker_by_code_count}")
        print(f"   └─ Tìm thấy qua tên công ty: {ticker_by_company_count}")

        print("🏷️ Đang gán sector...")
        tag_sectors.run(preprocessed_articles)
        total_sector_tags = sum(len(a.get("sectors", [])) for a in preprocessed_articles)
        print(f"🔢 Tổng số sector được gán: {total_sector_tags}")

        print("🔍 Đang phân tích cảm xúc...")
        enriched_articles = analyze_sentiment_per_entity.run(preprocessed_articles)

        print("💾 Đang ghi sentiment vào database...")
        update_sentiment_to_db(enriched_articles, db)

        print("🎉 Hoàn tất pipeline với dữ liệu thử nghiệm.")

    finally:
        db.close()

if __name__ == "__main__":
    run(limit_test=30000)

