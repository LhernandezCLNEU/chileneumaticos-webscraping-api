from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class ParsedResult(Base):
    __tablename__ = "parsed_results"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    title_format_id = Column(Integer, ForeignKey("title_formats.id"), nullable=True)
    result = Column(JSON, nullable=True)
    confidence = Column(Integer, nullable=True)
    parsed_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="parsed_results")
    title_format = relationship("TitleFormat", back_populates="parsed_results")
