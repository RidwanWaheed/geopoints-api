from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from typing import List, Optional, Tuple

from app.models.point import Point
from app.spatial.utils import point_to_geojson
from app.repositories.point import PointRepository
from app.schemas.point import PointCreate, PointUpdate, Point as PointSchema, NearbyPoint


class PointService:
    def __init__(self, repository: PointRepository):
        self.repository = repository

    def create(self, db: Session, *, obj_in: PointCreate) -> Point:
        """Create a new point"""
        return self.repository.create_with_coords(db=db, obj_in=obj_in)
    
    def get(self, db: Session, *, id: int) -> Optional[Point]:
        """Get point by ID"""
        return self.repository.get(db=db, id=id)
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[Point]:
        """Get multiple points with optional category filter"""
        if category_id:
            return self.repository.get_by_category(db=db, category_id=category_id, skip=skip, limit=limit)
        return self.repository.get_multi(db=db, skip=skip, limit=limit)
    
    def update(self, db: Session, *, db_obj: Point, obj_in: PointUpdate) -> Point:
        """Update a point"""
        return self.repository.update(db=db, db_obj=db_obj, obj_in=obj_in)
    
    def remove(self, db: Session, *, id: int) -> Point:
        """Remove a point"""
        return self.repository.remove(db=db, id=id)
    
    def get_nearby(self, db: Session, *, lat: float, lng: float, radius: float, limit: int = 100) -> List[NearbyPoint]:
        """Get points within a specified radius of a location"""
        results = []
        for point_obj, distance in self.repository.get_nearby(db=db, lat=lat, lng=lng, radius=radius, limit=limit):
            # Convert to Pydantic model
            point_schema = PointSchema.model_validate(point_obj)
            # Add the GeoJSON coordinates
            point_schema.coordinates = point_to_geojson(point_obj.geometry)
            # Create NearbyPoint with distance
            nearby_point = NearbyPoint(**point_schema.model_dump(), distance=distance)
            results.append(nearby_point)

        return results
    
    def get_within_polygon(self, db: Session, *, polygon: str, limit: int = 100) -> List[Point]:
        """Get points within a polygon defined in WKT format"""
        # Query points using PostGIS ST_Within
        query = db.query(Point).filter(
            func.ST_Within(
                Point.geometry,
                func.ST_GeomFromText(polygon, 4326)
            )
        ).limit(limit)

        results = []
        for point_obj in query.all():
          # Convert to Pydantic model
          point_schema = PointSchema.model_validate(point_obj)  
          # Add the GeoJSON coordinates
          point_schema.coordinates = point_to_geojson(point_obj.geometry)
          results.append(point_schema)

        return results
        

    def get_nearest(self, db: Session, *, lat: float, lng: float, limit: int = 5) -> List[NearbyPoint]:
        """Get the nearest points to a location"""
        results = []
        for point_obj, distance in self.repository.get_nearest(db=db, lat=lat, lng=lng, limit=limit):
            # Convert to Pydantic model
            point_schema = PointSchema.model_validate(point_obj)
            # Add the GeoJSON coordinates
            point_schema.coordinates = point_to_geojson(point_obj.geometry)
            results.append(point_schema)

        return results
    
    def count(self, db: Session, *, category_id: Optional[int] = None) -> int:
        """Count total points with optional category filter"""
        query = db.query(func.count(Point.id))
        if category_id:
            query = query.filter(Point.category_id == category_id)
        return query.scalar()


