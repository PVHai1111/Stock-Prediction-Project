import feedparser
import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

rss_url = "https://vietstock.vn/830/chung-khoan/co-phieu.rss"
save_path = f"vietstock_articles_{datetime.today().strftime('%Y-%m-%d')}.json"

feed = feedparser.parse(rss_url)
articles = []

for entry in feed.entries:
    try:
        url = entry.link
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        content_block = soup.find("div", {"data-role": "content"})
        paragraphs = content_block.find_all("p") if content_block else []
        full_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        articles.append({
            "title": entry.title,
            "link": url,
            "published_time": entry.published,
            "summary": entry.description,
            "content": full_text
        })

        print(f"✅ {entry.title}")
        time.sleep(0.1)

    except Exception as e:
        print(f"❌ Lỗi: {e}")

# Lưu lại file
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã lưu {len(articles)} bài vào {save_path}")
