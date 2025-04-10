import pandas as pd
import json
import os

ticker = "FPT"

# 1. Đọc dữ liệu giá
price_df = pd.read_csv(f"stock_price_history_crawl/{ticker}_historical_data.csv")
price_df["Date"] = pd.to_datetime(price_df["Date"], format="%d/%m/%Y")
price_df = price_df.sort_values("Date").reset_index(drop=True)

# 2. Đọc dữ liệu sentiment
with open("articles_with_sentiment.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# 3. Lọc bài viết chứa mã cổ phiếu
filtered_articles = [a for a in articles if ticker in a.get("tickers", [])]

# 4. Tạo DataFrame từ bài viết
articles_df = pd.DataFrame(filtered_articles)
articles_df["Date"] = pd.to_datetime(articles_df["date"])

# 5. Đếm số bài theo từng sentiment mỗi ngày
sentiment_counts = articles_df.groupby(["Date", "sentiment"]).size().unstack(fill_value=0)
sentiment_counts["total_articles"] = sentiment_counts.sum(axis=1)
sentiment_counts = sentiment_counts.rename(columns={"POS": "positive", "NEG": "negative", "NEU": "neutral"}).reset_index()

# 6. Merge sentiment vào giá
merged = pd.merge(price_df, sentiment_counts, on="Date", how="left")
merged[["positive", "negative", "neutral", "total_articles"]] = merged[["positive", "negative", "neutral", "total_articles"]].fillna(0)

# 7. Tính Target_Label dựa vào sự thay đổi giá Close ngày kế tiếp
merged = merged.sort_values("Date").reset_index(drop=True)
merged["Next_Close"] = merged["Close"].shift(-1)

def label_func(row):
    if pd.isna(row["Next_Close"]):
        return None
    if row["Next_Close"] > row["Close"]:
        return 1
    elif row["Next_Close"] < row["Close"]:
        return -1
    else:
        return 0

merged["Target_Label"] = merged.apply(label_func, axis=1)
merged = merged.drop(columns=["Next_Close"])

# 8. Lưu kết quả
os.makedirs("merge_price_sentiment", exist_ok=True)
merged.to_csv(f"merge_price_sentiment/{ticker}_final_training_data.csv", index=False)

print(f"✅ Đã tạo DataFrame huấn luyện với {len(merged.dropna())} dòng dữ liệu.")
print(f"📁 Đường dẫn: merge_price_sentiment/{ticker}_final_training_data.csv")