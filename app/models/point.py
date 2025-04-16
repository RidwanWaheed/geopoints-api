from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.base import Base


class Point(Base):
    __tablename__ = "point"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category = relationship("Category", back_populates="points")
