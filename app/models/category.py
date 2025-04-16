from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.base import Base
from app.core.utils import utc_now


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.current_timestamp()))
    updated_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.current_timestamp()), 
                   onupdate=func.timezone('UTC', func.current_timestamp()))

    points = relationship("Point", back_populates="category")
