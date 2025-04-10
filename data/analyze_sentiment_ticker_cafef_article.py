import json
from collections import defaultdict
import pandas as pd

# Map nhãn viết tắt sang đầy đủ
sentiment_map = {
    "POS": "positive",
    "NEU": "neutral",
    "NEG": "negative"
}

# Load dữ liệu
with open("articles_with_sentiment.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Khởi tạo thống kê
ticker_stats = defaultdict(lambda: {"count": 0, "positive": 0, "neutral": 0, "negative": 0})

# Duyệt qua từng bài viết
for article in articles:
    tickers = article.get("tickers", [])
    raw_sentiment = article.get("sentiment", "").upper()
    sentiment = sentiment_map.get(raw_sentiment, "neutral")  # Mặc định là neutral nếu lỗi

    for ticker in tickers:
        ticker_stats[ticker]["count"] += 1
        ticker_stats[ticker][sentiment] += 1

# Chuyển sang DataFrame để dễ phân tích
df = pd.DataFrame.from_dict(ticker_stats, orient="index")
df.index.name = "Ticker"
df = df.reset_index()
df = df.sort_values(by="count", ascending=False)

# Lưu kết quả
df.to_csv("ticker_sentiment_stats.csv", index=False, encoding="utf-8-sig")
print("✅ Đã lưu thống kê vào 'ticker_sentiment_stats.csv'")

