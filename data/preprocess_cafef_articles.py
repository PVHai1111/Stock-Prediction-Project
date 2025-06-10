#preprocess_cafef_articles.py
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os

# === Đường dẫn ===
input_path = "cafef_articles/2025-04-22/articles_combined.json"
ticker_path = "company_ticker_list.json"
output_path = "articles_preprocessed.json"

extra_indexes = {
    "VNINDEX", "VN30", "HNXINDEX", "HNX30", "UPCOMINDEX", "VNXALL", "VNX100"
}

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text

# === Load dữ liệu ===
with open(input_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

with open(ticker_path, "r", encoding="utf-8") as f:
    ticker_list = json.load(f)

ticker_map = {item["ticker"].upper(): item["company"].lower() for item in ticker_list}
name_to_ticker = {v: k for k, v in ticker_map.items()}

seen_titles = set()
cleaned_articles = []

for article in articles:
    title = clean_text(article.get("title", ""))
    content = clean_text(article.get("content", ""))
    sapo = clean_text(article.get("sapo", ""))
    summary = clean_text(article.get("summary", ""))

    if not any([title, content, sapo, summary]):
        print(f"🗑️ Bỏ bài không có nội dung: {title}")
        continue

    # Chuẩn hóa ngày
    raw_date = article.get("published_time", "")
    try:
        date_obj = datetime.strptime(raw_date, "%d-%m-%Y - %H:%M %p")
    except ValueError:
        try:
            date_obj = datetime.fromisoformat(raw_date)
        except ValueError:
            print(f"🗑️ Bỏ bài lỗi ngày tháng: {title} -> {raw_date}")
            continue

    article["published_time"] = date_obj.strftime("%Y-%m-%d")

    # Tìm ticker
    tickers = set()

    # 1. Từ data-symbol (nếu có)
    if "data-symbol" in article:
        tickers.add(article["data-symbol"].strip().upper())

    # 2. Từ nội dung (ticker hoặc tên công ty)
    full_text = f"{title} {sapo} {summary} {content}".lower()
    for ticker, name in ticker_map.items():
        if ticker.lower() in full_text or name in full_text:
            tickers.add(ticker)

    for idx in extra_indexes:
        if idx.lower() in full_text:
            tickers.add(idx)

    # Ghi lại thông tin đã làm sạch
    article["title"] = title
    article["summary"] = summary
    article["sapo"] = sapo
    article["content"] = content
    article["tickers"] = sorted(list(tickers))

    cleaned_articles.append(article)

# === Ghi ra file kết quả ===
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_articles, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã tiền xử lý {len(cleaned_articles)} bài viết và lưu vào: {output_path}")




