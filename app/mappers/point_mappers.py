from typing import Any, Dict, List, Tuple

from app.models.point import Point
from app.schemas.point import NearbyPoint
from app.schemas.point import Point as PointSchema
from app.core.utils import point_to_geojson


class PointMapper:
    """
    Mapper class responsible for transforming between database models and API schemas
    for Point entities.
    """

    @staticmethod
    def to_schema(db_obj: Point) -> PointSchema:
        """
        Convert a Point database model to a Point schema.
        """
        if not db_obj:
            return None

        # Convert to dict with basic fields
        db_dict = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}

        # Convert geometry to GeoJSON format
        db_dict["coordinates"] = point_to_geojson(db_obj.geometry)

        # Remove geometry as it's not in the Pydantic schema
        db_dict.pop("geometry", None)

        # Add category if available
        if db_obj.category:
            db_dict["category"] = {
                "id": db_obj.category.id,
                "name": db_obj.category.name,
                "description": db_obj.category.description,
                "color": db_obj.category.color,
            }

        # Create Pydantic model
        return PointSchema(**db_dict)

    @staticmethod
    def to_schema_with_distance(
        point_with_distance: Tuple[Point, float],
    ) -> NearbyPoint:
        """
        Convert a (Point, distance) tuple to a NearbyPoint schema.
        """
        point_obj, distance = point_with_distance

        # First convert to standard point schema
        point_dict = PointMapper.to_schema(point_obj).dict()

        # Add distance
        point_dict["distance"] = distance

        # Create NearbyPoint
        return NearbyPoint(**point_dict)

    @staticmethod
    def to_schema_list(db_objs: List[Point]) -> List[PointSchema]:
        """
        Convert a list of Point database models to a list of Point schemas.
        """
        return [PointMapper.to_schema(db_obj) for db_obj in db_objs]

    @staticmethod
    def to_nearby_point_list(
        points_with_distance: List[Tuple[Point, float]],
    ) -> List[NearbyPoint]:
        """
        Convert a list of (Point, distance) tuples to a list of NearbyPoint schemas.
        """
        return [
            PointMapper.to_schema_with_distance(item) for item in points_with_distance
        ]
