from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.base import Base
from app.core.constants import SpatialRefSys


class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    geometry = Column(
        Geometry(geometry_type="POINT", srid=SpatialRefSys.WGS84), nullable=False
    )
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.current_timestamp()),
        onupdate=func.timezone("UTC", func.current_timestamp()),
    )

    category = relationship("Category", back_populates="points")
