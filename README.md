# Stock Prediction Web App

Dự án này là một hệ thống web app dự đoán xu hướng giá cổ phiếu dựa trên dữ liệu tin tức và giá lịch sử. Dự án bao gồm các chức năng:

- Thu thập và hiển thị tin tức tài chính mới nhất
- Thu thập và hiển thị lịch sử giá cổ phiếu mới nhấtnhất
- Phân tích cảm xúc bài viết cho từng mã cổ phiếu/ngành
- Huấn luyện và dự đoán xu hướng tăng/giảm cổ phiếu
- Hiển thị thông tin liên hệ và thông số đánh giá cho từng dự đoán
- Hỗ trợ chọn mô hình dự đoán: Random Forest, XGBoost, LightGBM

## Kiến trúc hệ thống

```
🔹 app/                        # Backend FastAPI
🔹 data/                      # Dữ liệu tĩnh (mapping, json crawl)
🔹 frontend/stock-webapp/    # Frontend React (Vite + Tailwind)
```

## Các công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: ReactJS (Vite), TailwindCSS
- **ML**: Scikit-learn, XGBoost, LightGBM
- **NLP**: PhoBERT (wonrax/phobert-base-vietnamese-sentiment)
- **Crawl**: Requests, Selenium (cho Vietstock), BeautifulSoup

## Cài đặt

```bash
# Clone repo
$ git clone https://github.com/your-username/stock-predict-webapp.git
$ cd stock-predict-webapp
```

### 1. Backend

```bash
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Tạo PostgreSQL DB:

```sql
CREATE USER stockuser WITH PASSWORD 'password';
CREATE DATABASE stockdb OWNER stockuser;
```

Tạo bảng:

```bash
alembic upgrade head
```

### 2. Frontend

```bash
cd frontend/stock-webapp
npm install
npm run dev
```

Truy cập: [http://localhost:5173](http://localhost:5173)

### 3. Chạy backend

```bash
cd app
uvicorn main:app --reload
```

## Pipeline tiếu chuẩn

### Cập nhật giá & tin tức

```bash
python3 -m app.tasks.prices_pipeline.run_pipeline
python3 -m app.tasks.news_pipeline.run_pipeline
```

### Gán nhãn ticker/sector & sentiment

```bash
python3 -m app.tasks.news_pipeline.run_full_annotation
```

### Dự đoán

```bash
python3 -m app.tasks.model_pipeline.run_prediction_pipeline FPT xgboost
```

## Tính năng

- `News`: Xem danh sách tin tức mới
- `Price History`: Biểu đồ giá + số bài sentiment/ngày
- `Prediction`: Dự đoán tăng/giảm + mô hình + giải thích

## Credit

Phạm Việt Hải – HEDSPI, HUST\
Email: [hai.pv215044@hust.edu.vn](mailto\:hai.pv215044@hust.edu.vn)\
GitHub: [https://github.com/PVHai1111](https://github.com/PVHai1111)