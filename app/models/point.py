from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func
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
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
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

    # Define indexes using SQLAlchemy
    __table_args__ = (
        Index('idx_points_geometry', 'geometry', postgresql_using='gist'),
        Index('idx_points_geography', func.geography('geometry'), postgresql_using='gist'),
        # KNN index can't be defined directly in SQLAlchemy, SQL written in the migration file
    )