from transformers import RobertaForSequenceClassification, AutoTokenizer
from underthesea import word_tokenize
import torch
import torch.nn.functional as F
import json

# Load mô hình sentiment đã fine-tune sẵn
model_name = "wonrax/phobert-base-vietnamese-sentiment"
model = RobertaForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

# Hàm dự đoán cảm xúc từ text
def predict_sentiment(text):
    segmented = word_tokenize(text, format="text")
    inputs = tokenizer(segmented, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        label = torch.argmax(probs).item()
        score = probs[0][label].item()
    labels = ["NEG", "POS", "NEU"]  # Negative, Positive, Neutral
    return labels[label], round(score, 3)

# Load dữ liệu đã được tiền xử lý
with open("articles_preprocessed.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Phân tích cảm xúc từng bài viết
for article in articles:
    text = article.get("sapo") or article.get("summary") or article.get("content") or ""
    try:
        label, confidence = predict_sentiment(text)
    except Exception as e:
        print(f"❌ Lỗi bài viết '{article.get('title')}': {e}")
        label, confidence = "NEU", 0.0
    article["sentiment"] = label
    article["sentiment_confidence"] = confidence

# Lưu kết quả ra file
with open("articles_with_sentiment.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print("✅ Đã phân tích xong cảm xúc cho các bài viết.")
