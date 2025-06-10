# app/tasks/news_pipeline/preprocess_articles.py

import re
from bs4 import BeautifulSoup
from datetime import datetime

def clean_text(text: str, keep_case: bool = True) -> str:
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text if keep_case else text.lower()

def parse_date(raw_date: str) -> str:
    """
    Chuyển đổi chuỗi ngày về định dạng YYYY-MM-DD nếu có thể.
    Trả về None nếu không parse được.
    """
    raw_date = raw_date.strip()

    # Nếu đã đúng định dạng chuẩn
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        return raw_date

    # Danh sách định dạng ngày cần thử
    formats = [
        "%d-%m-%Y - %I:%M %p",  # 22-04-2025 - 09:31 AM
        "%d-%m-%Y - %H:%M",     # 22-04-2025 - 14:45
        "%Y-%m-%dT%H:%M:%S",    # 2025-04-22T19:01:00
        "%Y-%m-%d %H:%M:%S",    # 2025-04-22 19:01:00
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(raw_date, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Thử parse ISO tự động
    try:
        return datetime.fromisoformat(raw_date).strftime("%Y-%m-%d")
    except Exception:
        return None

def run(articles: list[dict]) -> list[dict]:
    cleaned_articles = []

    for article in articles:
        title = clean_text(article.get("title", ""), keep_case=True)
        content = clean_text(article.get("content", ""), keep_case=True)
        sapo = clean_text(article.get("sapo", ""), keep_case=True)
        summary = clean_text(article.get("summary", ""), keep_case=True)

        if not any([title, content, sapo, summary]):
            print(f"🗑️ Bỏ bài không có nội dung: {article.get('link', '')}")
            continue

        raw_date = article.get("published_time", "")
        parsed_date = parse_date(raw_date)

        if not parsed_date:
            print(f"🗑️ Bỏ bài lỗi ngày tháng: {title} → {raw_date}")
            continue

        article.update({
            "title": title,
            "summary": summary,
            "sapo": sapo,
            "content": content,
            "published_time": parsed_date,
        })

        cleaned_articles.append(article)

    print(f"✅ Đã tiền xử lý {len(cleaned_articles)} / {len(articles)} bài viết.")
    return cleaned_articles
