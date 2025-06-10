# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import news, prices, predictions

app = FastAPI()

# ✅ Cho phép truy cập từ frontend React (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Đăng ký các route
app.include_router(news.router)
app.include_router(prices.router)
app.include_router(predictions.router)


