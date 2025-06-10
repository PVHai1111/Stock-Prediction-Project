# app/models/price.py

from sqlalchemy import Column, Integer, Float, String, Date, BigInteger 
from app.db import Base

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)          
    trade_value = Column(BigInteger)     


