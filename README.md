# Stock-Prediction-Project

## Tiến trình

### Thu thập dữ liệu:
- **FireAnt**:
  - Bình luận: `data/crawl_fireant_comment.py`
  - Lịch sử giá cổ phiếu: `data/stock_price_history_crawl`
- **CafeF**:
  - Tin tức: `data/crawl_cafef_news.py`

### Xử lý dữ liệu:
- **Tin tức CafeF**:
  - Gán mã cổ phiếu, chuẩn hóa ngày đăng, làm sạch dữ liệu: `data/preprocess_cafef_articles.py`
  - Gán chỉ số sentiment: `data/predict_sentiment_cafef_articles.py`

### Dữ liệu cuối sử dụng:
- Lịch sử giá cổ phiếu: `data/stock_price_history_crawl`
- Tin tức gán chỉ số sentiment: `data/articles_with_sentiment.json`

### Mô hình:
- Thư mục `code`

### Vấn đề:
- Dữ liệu chưa đủ (mới chỉ ~1 năm)
- Chỉ số sentiment chưa chắc chắn độ chính xác
- Độ chính xác của các thử nghiệm trên model còn thấp (<40%)


