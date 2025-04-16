from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text

from app.base import Base


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)

    points = relationship("Point", back_populates="category")
