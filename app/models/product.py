from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(128), index=True, nullable=True)
    title_raw = Column(Text, nullable=False)
    title_normalized = Column(Text, nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    specs = Column(JSON, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(8), nullable=True)
    url = Column(String(2000), nullable=True)
    source = Column(String(255), nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")
    tire_spec = relationship("TireSpec", uselist=False, back_populates="product")
    parsed_results = relationship("ParsedResult", back_populates="product")
