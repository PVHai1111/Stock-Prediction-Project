# app/models/news.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.db import Base
from .news_ticker_mapping import NewsTickerMapping
from .news_sector_mapping import NewsSectorMapping

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)
    published_time = Column(DateTime)
    summary = Column(Text)
    price_change_info = Column(Text)
    category = Column(String)
    sapo = Column(Text)
    content = Column(Text)
    source = Column(String, nullable=True)

    tickers = relationship(
        "NewsTickerMapping",
        back_populates="news",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    sector_mappings = relationship("NewsSectorMapping", back_populates="news")




