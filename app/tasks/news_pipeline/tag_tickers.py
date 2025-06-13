# app/tasks/news_pipeline/tag_tickers.py

import json
import os
import re
from underthesea import sent_tokenize

EXTRA_INDEXES = {
    # Có thể thêm các index đặc biệt khác ở đây nếu cần
}

# Load danh sách mã và tên công ty
TICKER_PATH = os.path.join("data", "company_ticker_list.json")
with open(TICKER_PATH, "r", encoding="utf-8") as f:
    ticker_list = json.load(f)

# Map: ticker → tên công ty (lower case, bỏ phần ngoặc)
ticker_map = {}
for item in ticker_list:
    raw_name = item["company"]
    cleaned_name = re.sub(r"\s*\(.*?\)", "", raw_name).strip().lower()
    ticker_map[item["ticker"].upper()] = cleaned_name

def run(articles: list[dict]) -> list[dict]:
    for article in articles:
        ticker_dict = {}
        ticker_sentences = {}

        # Ưu tiên gán nếu có sẵn trường data-symbol
        if "data-symbol" in article and article["data-symbol"]:
            code = article["data-symbol"].strip().upper()
            ticker_dict[code] = {
                "ticker": code,
                "sentences": [],
                "source": "code"
            }

        full_text = f"{article.get('title', '')} {article.get('sapo', '')} {article.get('summary', '')} {article.get('content', '')}"
        sentences = sent_tokenize(full_text)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            for ticker, company_name in ticker_map.items():
                # ✅ So khớp chính xác ticker viết hoa, được phân tách bằng ký tự không phải chữ cái (dùng regex)
                pattern = rf"(?<![A-Z])\b{ticker}\b(?![A-Z])"
                if re.search(pattern, sentence):
                    if ticker not in ticker_dict:
                        ticker_dict[ticker] = {
                            "ticker": ticker,
                            "sentences": [],
                            "source": "code"
                        }
                    ticker_dict[ticker]["sentences"].append(sentence.strip())

                # Nếu không tìm thấy ticker thì mới kiểm tra tên công ty (lowercase)
                elif company_name in sentence_lower:
                    if ticker not in ticker_dict:
                        ticker_dict[ticker] = {
                            "ticker": ticker,
                            "sentences": [],
                            "source": "company"
                        }
                    ticker_dict[ticker]["sentences"].append(sentence.strip())

            # Gán theo index đặc biệt nếu có
            for index in EXTRA_INDEXES:
                if index in sentence:
                    if index not in ticker_dict:
                        ticker_dict[index] = {
                            "ticker": index,
                            "sentences": [],
                            "source": "code"
                        }
                    ticker_dict[index]["sentences"].append(sentence.strip())

        # Chuẩn hóa kết quả
        article["tickers"] = list(ticker_dict.values())
        article["ticker_sentences"] = {
            t["ticker"]: t["sentences"] for t in article["tickers"]
        }

        if not article["tickers"]:
            print(f"⚠️ Không tìm thấy ticker cho bài viết: {article.get('title', '')}")

    print(f"✅ Đã gán ticker và câu chứa mã cho {len(articles)} bài viết.")
    return articles




