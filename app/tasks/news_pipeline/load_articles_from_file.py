import json
from datetime import datetime
from app.db import SessionLocal
from app.models.news import News

def load_articles():
    db = SessionLocal()
    path = "data/cafef_articles/2025-04-22/articles_combined.json"
    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    inserted = 0
    for a in articles:
        if not a.get("title") or not a.get("link") or not a.get("published_time"):
            continue
        try:
            pub_time = datetime.strptime(a["published_time"], "%d-%m-%Y - %H:%M %p")
        except Exception:
            print(f"Lỗi thời gian: {a['title']} → {a['published_time']}")
            continue

        db.add(News(
            title=a.get("title", ""),
            link=a.get("link", ""),
            published_time=pub_time,
            summary=a.get("summary", ""),
            price_change_info=a.get("price_change_info", ""),
            category=a.get("category", ""),
            sapo=a.get("sapo", ""),
            content=a.get("content", ""),
            source="cafef"
        ))
        inserted += 1
    db.commit()
    db.close()
    print(f"✅ Đã thêm {inserted} bài viết vào bảng news.")

if __name__ == "__main__":
    load_articles()
