# app/models/news_ticker_mapping.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.db import Base
from sqlalchemy.orm import relationship


class NewsTickerMapping(Base):
    __tablename__ = "news_ticker_mapping"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"))
    ticker = Column(String, nullable=False, index=True) # e.g., "VND", "VIC", "FPT"
    sentiment = Column(String)       # "pos", "neg", "neu"
    confidence = Column(Float)     # e.g., '0.93'

    news = relationship("News", back_populates="tickers")



