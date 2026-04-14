from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class TitleFormat(Base):
    __tablename__ = "title_formats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    pattern = Column(Text, nullable=False)
    example = Column(Text, nullable=True)
    priority = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    version = Column(String(32), default="1.0")
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by = relationship("User", back_populates="title_formats")
    parsed_results = relationship("ParsedResult", back_populates="title_format")
