from typing import List, Optional, Tuple, Union

from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import SpatialRefSys
from app.models.point import Point
from app.repositories.base import BaseRepository
from app.schemas.point import PointCreate, PointUpdate
from app.spatial.queries import (
    add_distance_to_query,
    filter_by_distance,
    nearest_neighbor_query,
    point_to_ewkb,
)


class PointRepository(BaseRepository[Point, PointCreate, PointUpdate]):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Point)

    def create_from_coords(self, *, obj_in: PointCreate) -> Point:
        """Create a new point from coordinates in the PointCreate schema"""
        # Convert latitude and longitude to a shapely Point
        shapely_point = ShapelyPoint(obj_in.longitude, obj_in.latitude)

        # Create dictionary from pydantic model excluding lat/lng
        data = obj_in.model_dump(exclude={"latitude", "longitude"})

        # Create a new Point with PostGIS geometry
        db_obj = Point(
            **data, geometry=from_shape(shapely_point, srid=SpatialRefSys.WGS84)
        )

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)

        return db_obj

    def get_by_category(
        self, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Point]:
        """Get points filtered by category"""
        return (
            self.session.query(Point)
            .filter(Point.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_nearby(
        self, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[Tuple[Point, float]]:
        """Get points within a specified radius (in meters) of a location"""
        # Create EWKB point from coordinates
        wkb_point = point_to_ewkb(lat, lng)

        # Build query with optimized distance calculation and filtering
        query = self.session.query(Point)
        query = add_distance_to_query(query, Point, wkb_point)
        query = filter_by_distance(query, Point, wkb_point, radius)

        # Order by distance and limit results
        query = query.order_by("distance").limit(limit)

        return query.all()

    def get_within_polygon(self, *, polygon: str, limit: int = 100) -> List[Point]:
        """
        Get points within a polygon boundary defined as WKT
        Uses a spatial index optimization
        """
        # Use ST_MakeValid to ensure the polygon is valid
        # Then use && operator for index-assisted bounding box check first
        # Finally apply the more expensive ST_Within for precise filtering
        return (
            self.session.query(Point)
            .filter(
                Point.geometry.intersects(
                    func.ST_MakeValid(
                        func.ST_GeomFromText(polygon, SpatialRefSys.WGS84)
                    )
                )
            )
            .filter(
                func.ST_Within(
                    Point.geometry,
                    func.ST_MakeValid(
                        func.ST_GeomFromText(polygon, SpatialRefSys.WGS84)
                    ),
                )
            )
            .limit(limit)
            .all()
        )

    def get_nearest(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[Tuple[Point, float]]:
        """Get the nearest points to a location using KNN optimization"""
        # Create point from coordinates
        point_geom = point_to_ewkb(lat, lng)

        # Build query with optimized KNN search
        query = self.session.query(Point)
        query = add_distance_to_query(query, Point, point_geom)
        query = nearest_neighbor_query(query, Point, point_geom)
        query = query.limit(limit)

        return query.all()

    def count(self, *, category_id: Optional[int] = None) -> int:
        """Count total points with optional category filter"""
        query = self.session.query(func.count(Point.id))
        if category_id:
            query = query.filter(Point.category_id == category_id)
        return query.scalar()
