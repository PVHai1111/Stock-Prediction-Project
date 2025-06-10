# app/tasks/news_pipeline/run_pipeline.py

import time
import re
from datetime import datetime
from app.tasks.news_pipeline import (
    crawl_cafef,
    preprocess_articles,
    tag_tickers,
    tag_sectors,
    analyze_sentiment_per_entity,
    insert_to_db,
)
from app.db import SessionLocal
from app.models.news import News

SLEEP_INTERVAL = 6 * 60 * 60  # 6 tiếng


def already_exists(link: str) -> bool:
    db = SessionLocal()
    result = db.query(News).filter(News.link == link).first()
    db.close()
    return result is not None


def normalize_date(date_str: str) -> str:
    date_str = date_str.strip()

    # Nếu đã đúng định dạng YYYY-MM-DD thì trả về luôn
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str

    # Các định dạng khác có thể gặp
    date_str = re.sub(r" - 00:(\d{2}) AM", r" - 12:\1 AM", date_str)
    date_str = re.sub(r" - (\d{2}:\d{2})\s*(AM|PM)", r" - \1", date_str)

    formats = [
        "%d-%m-%Y - %I:%M %p",
        "%d-%m-%Y - %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except Exception:
        raise ValueError(f"Không thể parse ngày: {date_str}")


def run_once():
    print(f"\n🕒 Bắt đầu pipeline lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Crawl
    print("🚀 Đang thu thập tin tức từ CafeF...")
    articles = crawl_cafef.run()

    # Step 2: Lọc bài trùng & chuẩn hóa ngày
    filtered = []
    for art in articles:
        link = art.get("link", "")
        date_str = art.get("published_time", "")

        if already_exists(link):
            print(f"🔁 Bỏ qua bài đã có trong DB: '{art.get('title', '')}'")
            continue

        try:
            art["published_time"] = normalize_date(date_str)
        except Exception as e:
            print(f"❌ Lỗi ngày tháng: {art.get('title')} - {e}")
            continue

        filtered.append(art)

    if not filtered:
        print("❌ Không có bài mới nào để xử lý.")
        return

    # Step 3: Preprocess
    print(f"🧹 Đang làm sạch {len(filtered)} bài viết...")
    cleaned_articles = preprocess_articles.run(filtered)

    # Step 4: Tag tickers
    print("🏷️ Đang gán mã cho bài viết...")
    tagged_articles = tag_tickers.run(cleaned_articles)

    # Step 4.5: Tag sectors
    tagged_articles = tag_sectors.run(tagged_articles)

    # Step 5: Analyze sentiment
    print("Đang phân tích sentiments...")
    analyzed_articles = analyze_sentiment_per_entity.run(tagged_articles)

    # Step 6: Insert to DB
    print("💾 Đang ghi dữ liệu vào database...")
    insert_to_db.run(analyzed_articles)


def main_loop():
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"❌ Lỗi trong pipeline: {e}")
        print(f"⏳ Chờ 6 tiếng tiếp theo...\n")
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    # main_loop()
    run_once()
