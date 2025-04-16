from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint

from app.models.point import Point
from app.repositories.base import Baserepository
from app.schemas.point import PointCreate, PointUpdate


class PointRepository(Baserepository[Point, PointCreate, PointUpdate]):
    def __init__(self):
        super().__init__(Point)

    def create_with_coords(self, db: Session, *, obj_in: PointCreate) -> Point:
        """Create a new point with coordinates"""
        # Convert latitude and longitude to a shapely Point
        shapely_point = ShapelyPoint(obj_in.longitude, obj_in.latitude)

        # Create dictionary from pydantic model excluding lat/lng
        data = obj_in.model_dump(exclude={"latitude", "longitude"})

        # Create a new Point with PostGIS geometry
        db_obj = Point(**data, geometry=from_shape(shapely_point, srid=4326))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_by_category(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Point]:
        """Get points filtered by category"""
        db.query(Point).filter(Point.category_id == category_id).offset(skip).limit(
            limit
        ).all()

    def get_nearby(
        self, db: Session, *, lat: float, long: float, radius: float, limit: int = 100
    ) -> List[tuple]:
        """Get points within a specified radius (in meters) of a location"""
        # Create point from coordinates
        shapely_point = ShapelyPoint(long, lat)

        # Query points within radius using PostGIS ST_DWithin
        # Convert to Web Mercator (SRID 3857) for more accurate distance calculation
        query = (
            db.query(
                Point,
                func.ST_Distance(
                    func.ST_Transform(Point.geometry, 3857),
                    func.ST_Transform(
                        func.ST_GeomFromWKB(from_shape(shapely_point, srid=4326)), 3857
                    ),
                ).label("distance"),
            )
            .filter(
                func.ST_Within(
                    func.ST_Transform(Point.geometry, 3857),
                    func.ST_Transform(
                        func.ST_GeomFromEWKB(from_shape(shapely_point, srid=4326)), 3857
                    ),
                    radius,
                )
            )
            .order_by("distance")
            .limit(limit)
        )

        return query.all()

    def get_within_polygon(
        self, db: Session, *, polygon: str, limit: int = 100
    ) -> List[Point]:
        """Get points within a polygon boundary defined as WKT"""
        return (
            db.query(Point)
            .filter(func.ST_Within(Point.geometry, func.ST_GeomFromText(polygon, 4326)))
            .limit(limit)
            .all()
        )

    def get_nearest(
        self, db: Session, *, lat: float, lng: float, limit: int = 5
    ) -> List[tuple]:
        """Get the nearest points to a location"""
        # Create point from coordinates
        point = ShapelyPoint(lng, lat)

        # Query points ordered by distance
        query = (
            db.query(
                Point,
                func.Distance(
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
