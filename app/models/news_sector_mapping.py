# app/models/news_sector_mapping.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.db import Base


class NewsSectorMapping(Base):
    __tablename__ = "news_sector_mapping"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"))
    sector = Column(String, index=True) # "ngành ngân hàng", "ngành công nghệ", v.v.
    sentiment = Column(String) # "pos", "neg", "neu"
    confidence = Column(Float)
    
    news = relationship("News", back_populates="sector_mappings")
