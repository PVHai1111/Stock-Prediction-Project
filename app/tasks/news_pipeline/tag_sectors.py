# app/tasks/news_pipeline/tag_sectors.py
import json
import os
import re
from underthesea import sent_tokenize

SECTOR_PATH = os.path.join("data", "company_ticker_list.json")
with open(SECTOR_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Tạo mapping sector → list ticker và ngược lại
sector_to_tickers = {}
for item in data:
    sector = item["sector"].strip().lower()
    ticker = item["ticker"].upper()
    sector_to_tickers.setdefault(sector, set()).add(ticker)

def run(articles: list[dict]) -> list[dict]:
    for article in articles:
        full_text = f"{article.get('title', '')} {article.get('sapo', '')} {article.get('summary', '')} {article.get('content', '')}"
        sentences = sent_tokenize(full_text)

        matched_sectors = {}
        for sentence in sentences:
            for sector in sector_to_tickers:
                if sector in sentence.lower():
                    if sector not in matched_sectors:
                        matched_sectors[sector] = []
                    matched_sectors[sector].append(sentence.strip())

        article["sectors"] = sorted(matched_sectors.keys())
        article["sector_sentences"] = matched_sectors

        if matched_sectors:
            print(f"📌 Bài viết gắn sector: {article.get('title')} → {list(matched_sectors.keys())}")

    return articles
