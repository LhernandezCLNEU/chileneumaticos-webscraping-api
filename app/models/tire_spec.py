from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class TireSpec(Base):
    __tablename__ = "tire_specs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)

    width = Column(String(16), nullable=True)
    profile = Column(String(16), nullable=True)
    diameter = Column(String(16), nullable=True)
    load_index = Column(String(8), nullable=True)
    speed_rating = Column(String(8), nullable=True)
    season = Column(String(32), nullable=True)
    tread_pattern = Column(String(255), nullable=True)

    product = relationship("Product", back_populates="tire_spec")
