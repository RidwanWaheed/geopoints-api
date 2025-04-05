from app.database import Base
from app.models.base import BaseModel
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Text

class Point(Base, BaseModel):
    """Point of interest model with geospatial data"""

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)  # Fixed typo from "decsription"
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    # Relationship to category
    category = relationship("Category", back_populates="points")
