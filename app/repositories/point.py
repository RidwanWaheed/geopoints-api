from typing import List, Optional

from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.point import Point
from app.repositories.base import BaseRepository
from app.schemas.point import PointCreate, PointUpdate


class PointRepository(BaseRepository[Point, PointCreate, PointUpdate]):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Point)

    def create_with_coords(self, *, obj_in: PointCreate) -> Point:
        """Create a new point with coordinates"""
        # Convert latitude and longitude to a shapely Point
        shapely_point = ShapelyPoint(obj_in.longitude, obj_in.latitude)

        # Create dictionary from pydantic model excluding lat/lng
        data = obj_in.model_dump(exclude={"latitude", "longitude"})

        # Create a new Point with PostGIS geometry
        db_obj = Point(**data, geometry=from_shape(shapely_point, srid=4326))

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)

        return db_obj

    def get_by_category(
        self, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Point]:
        """Get points filtered by category"""
        return self.session.query(Point).filter(Point.category_id == category_id).offset(skip).limit(
            limit
        ).all()

    def get_nearby(
        self, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[tuple]:
        """Get points within a specified radius (in meters) of a location"""
        # Create point from coordinates
        shapely_point = ShapelyPoint(lng, lat)
        wkb_point = from_shape(shapely_point, srid=4326)

        # Query points within radius using PostGIS ST_DWithin
        # Convert to Web Mercator (SRID 3857) for more accurate distance calculation
        query = (
            (
                self.session.query(
                    Point,
                    func.ST_Distance(
                        func.ST_Transform(Point.geometry, 3857),
                        func.ST_Transform(wkb_point, 3857),
                    ).label("distance"),
                ).filter(
                    func.ST_DWithin(
                        func.ST_Transform(Point.geometry, 3857),
                        func.ST_Transform(wkb_point, 3857),
                        radius,
                    )
                )
            )
            .order_by("distance")
            .limit(limit)
        )

        return query.all()

    def get_within_polygon(
        self, *, polygon: str, limit: int = 100
    ) -> List[Point]:
        """Get points within a polygon boundary defined as WKT"""
        return (
            self.session.query(Point)
            .filter(func.ST_Within(Point.geometry, func.ST_GeomFromText(polygon, 4326)))
            .limit(limit)
            .all()
        )

    def get_nearest(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[tuple]:
        """Get the nearest points to a location"""
        # Create point from coordinates
        point = ShapelyPoint(lng, lat)

        # Query points ordered by distance
        query = (
            self.session.query(
                Point,
                func.ST_Distance(
                    func.ST_Transform(Point.geometry, 3857),
                    func.ST_Transform(
                        func.ST_GeomFromEWKB(from_shape(point, srid=4326)), 3857
                    ),
                ).label("distance"),
            )
            .order_by("distance")
            .limit(limit)
        )

        return query.all()
    
    def count(self, *, category_id: Optional[int] = None) -> int:
        """Count total points with optional category filter"""
        query = self.session.query(func.count(Point.id))
        if category_id:
            query = query.filter(Point.category_id == category_id)
        return query.scalar()
