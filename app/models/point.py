from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.base import Base


class Point(Base):
    __tablename__ = "point"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326, nullable=False))
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    category = relationship("Category", back_populates="points")
