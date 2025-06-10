# app/tasks/news_pipeline/analyze_sentiment_per_entity.py
import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer
from underthesea import word_tokenize
import numpy as np
import torch.nn.functional as F
from tqdm import tqdm

# Cấu hình thiết bị
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.set_num_threads(8)  # Dùng tối đa 8 luồng CPU, có thể chỉnh tùy CPU bạn

# Tải model PhoBERT và tokenizer
MODEL_NAME = "wonrax/phobert-base-vietnamese-sentiment"
model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
model.eval()

LABELS = ["NEG", "POS", "NEU"]  # PhoBERT label order

# Cache kết quả sentiment để tránh lặp lại
sentiment_cache = {}

def batch_predict(sentences: list[str], batch_size: int = 128):
    results = []

    for i in tqdm(range(0, len(sentences), batch_size), desc="🚀 Đang batch-predict sentiment"):
        batch = sentences[i:i + batch_size]
        segmented = [word_tokenize(s, format="text") if s else "" for s in batch]

        inputs = tokenizer(
            segmented,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=256
        )

        # Chuyển dữ liệu sang thiết bị phù hợp (GPU hoặc CPU)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            preds = torch.argmax(probs, dim=-1)

        for idx in range(len(batch)):
            label_idx = preds[idx].item()
            confidence = round(probs[idx][label_idx].item(), 3)
            label = LABELS[label_idx].lower()
            results.append((label, confidence))

    return results


def run(articles: list[dict]) -> list[dict]:
    all_sentences = []
    for article in articles:
        all_sentences.extend(
            s for lst in article.get("ticker_sentences", {}).values() for s in lst
        )
        all_sentences.extend(
            s for lst in article.get("sector_sentences", {}).values() for s in lst
        )

    # Loại bỏ trùng lặp để dự đoán một lần duy nhất
    unique_sentences = list({s for s in all_sentences if s and s.strip()})
    print(f"🔍 Tổng số câu duy nhất cần phân tích: {len(unique_sentences)}")

    # Batch predict cho tất cả các câu duy nhất
    predictions = batch_predict(unique_sentences)

    # Gán vào cache
    for sentence, (sentiment, conf) in zip(unique_sentences, predictions):
        sentiment_cache[sentence] = (sentiment, conf)

    print("✅ Đã tạo xong cache. Đang gán kết quả vào từng bài viết...")

    for article in tqdm(articles, desc="🧠 Đang gán kết quả sentiment"):
        ticker_sentiments = {}
        sector_sentiments = {}

        for ticker, sentences in article.get("ticker_sentences", {}).items():
            best_sentiment, best_conf = None, -1
            for s in sentences:
                sentiment, conf = sentiment_cache.get(s, ("neu", 0.0))
                if conf > best_conf:
                    best_sentiment, best_conf = sentiment, conf
            if best_sentiment:
                ticker_sentiments[ticker] = {
                    "sentiment": best_sentiment,
                    "confidence": str(best_conf)
                }

        for sector, sentences in article.get("sector_sentences", {}).items():
            best_sentiment, best_conf = None, -1
            for s in sentences:
                sentiment, conf = sentiment_cache.get(s, ("neu", 0.0))
                if conf > best_conf:
                    best_sentiment, best_conf = sentiment, conf
            if best_sentiment:
                sector_sentiments[sector] = {
                    "sentiment": best_sentiment,
                    "confidence": str(best_conf)
                }

        article["ticker_sentiments"] = ticker_sentiments
        article["sector_sentiments"] = sector_sentiments

    print("🎉 Hoàn tất gán sentiment cho toàn bộ bài viết.")
    return articles


