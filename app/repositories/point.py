from typing import Any, Dict, List, Optional, Tuple

from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.constants import SpatialRefSys
from app.models.point import Point
from app.spatial.queries import (
    add_distance_to_query,
    filter_by_distance,
    nearest_neighbor_query,
    point_to_ewkb,
)


class PointRepository:
    """Repository for Point entities with GIS capabilities"""

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int) -> Optional[Point]:
        return self.session.query(Point).filter(Point.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[Point]:
        return self.session.query(Point).offset(skip).limit(limit).all()

    def create(self, *, obj_data: Dict[str, Any]) -> Point:
        db_obj = Point(**obj_data)
        self.session.add(db_obj)
        return db_obj

    def create_with_coordinates(
        self,
        *,
        name: str,
        description: Optional[str],
        latitude: float,
        longitude: float,
        category_id: Optional[int] = None,
    ) -> Point:
        shapely_point = ShapelyPoint(longitude, latitude)

        point = Point(
            name=name,
            description=description,
            geometry=from_shape(shapely_point, srid=SpatialRefSys.WGS84),
            category_id=category_id,
        )

        self.session.add(point)
        return point

    def update(self, *, db_obj: Point, obj_data: Dict[str, Any]) -> Point:
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def update_coordinates(
        self, *, point_id: int, latitude: float, longitude: float
    ) -> Optional[Point]:
        point = self.get(id=point_id)
        if not point:
            return None

        shapely_point = ShapelyPoint(longitude, latitude)
        point.geometry = from_shape(shapely_point, srid=SpatialRefSys.WGS84)

        self.session.add(point)
        self.session.flush()
        return point

    def delete(self, *, id: int) -> Optional[Point]:
        obj = self.get(id=id)
        if not obj:
            return None

        self.session.delete(obj)
        self.session.flush()
        return obj

    def count(self) -> int:
        return self.session.query(func.count(Point.id)).scalar()

    def get_by_category(
        self, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Point]:
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
        wkb_point = point_to_ewkb(lat, lng)

        query = self.session.query(Point)
        query = add_distance_to_query(query, Point, wkb_point)
        query = filter_by_distance(query, Point, wkb_point, radius)

        query = query.order_by(text("distance")).limit(limit)

        return query.all()

    def get_nearest(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[Tuple[Point, float]]:
        point_geom = point_to_ewkb(lat, lng)

        query = self.session.query(Point)
        query = add_distance_to_query(query, Point, point_geom)
        query = nearest_neighbor_query(query, Point, point_geom)
        query = query.limit(limit)

        return query.all()

    def get_within_polygon(self, *, polygon_wkt: str, limit: int = 100) -> List[Point]:
        return (
            self.session.query(Point)
            .filter(
                func.ST_Within(
                    Point.geometry,
                    func.ST_GeomFromText(polygon_wkt, SpatialRefSys.WGS84),
                )
            )
            .limit(limit)
            .all()
        )

    def count_by_category(self, *, category_id: int) -> int:
        return (
            self.session.query(func.count(Point.id))
            .filter(Point.category_id == category_id)
            .scalar()
        )
