from typing import List, Optional

from app.mappers.point_mappers import PointMapper
from app.repositories.point import PointRepository
from app.schemas.point import NearbyPoint, Point as PointSchema, PointCreate, PointUpdate


class PointService:
    def __init__(self, repository: PointRepository):
        self.repository = repository

    def create(self, *, obj_in: PointCreate) -> PointSchema:
        """Create a new point"""
        db_obj = self.repository.create_from_coords(obj_in=obj_in)
        return PointMapper.to_schema(db_obj)

    def get(self, *, id: int) -> Optional[PointSchema]:
        """Get point by ID"""
        db_obj = self.repository.get(id=id)
        return PointMapper.to_schema(db_obj)

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> List[PointSchema]:
        """Get multiple points with optional category filter"""
        if category_id:
            db_objs = self.repository.get_by_category(
                category_id=category_id, skip=skip, limit=limit
            )
        else:
            db_objs = self.repository.get_multi(skip=skip, limit=limit)

        return PointMapper.to_schema_list(db_objs)

    def update(self, *, id: int, obj_in: PointUpdate) -> Optional[PointSchema]:
        """Update a point"""
        db_obj = self.repository.get(id=id)
        if not db_obj:
            return None
        updated_obj = self.repository.update(db_obj=db_obj, obj_in=obj_in)
        return PointMapper.to_schema(updated_obj)

    def remove(self, *, id: int) -> Optional[PointSchema]:
        """Remove a point"""
        db_obj = self.repository.get(id=id)
        if not db_obj:
            return None
        removed_obj = self.repository.remove(id=id)
        return PointMapper.to_schema(removed_obj)

    def get_nearby(
        self, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[NearbyPoint]:
        """Get points within a specified radius of a location"""
        point_tuples = self.repository.get_nearby(
            lat=lat, lng=lng, radius=radius, limit=limit
        )
        return PointMapper.to_nearby_point_list(point_tuples)

    def get_within_polygon(
        self, *, polygon: str, limit: int = 100
    ) -> List[PointSchema]:
        """Get points within a polygon defined in WKT format"""
        point_objs = self.repository.get_within_polygon(
            polygon=polygon, limit=limit
        )
        return PointMapper.to_schema_list(point_objs)

    def get_nearest(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[NearbyPoint]:
        """Get the nearest points to a location"""
        point_tuples = self.repository.get_nearest(lat=lat, lng=lng, limit=limit)
        return PointMapper.to_nearby_point_list(point_tuples)

    def count(self, *, category_id: Optional[int] = None) -> int:
        """Count total points with optional category filter"""
        return self.repository.count(category_id=category_id)