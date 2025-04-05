from app.database import Base
from app.models.base import BaseModel
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship


class Category(Base, BaseModel):
    """Category model for points of interest"""

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    color = Column(String(7), nullable=True)

    # Relationship to points
    points = relationship("Point", back_populates="category")


    