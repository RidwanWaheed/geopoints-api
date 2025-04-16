from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from geoalchemy2.shape import to_shape
from geojson_pydantic import Point as GeoJSONPoint
from pydantic import BaseModel


def point_to_geojson(geometry):
    """Convert PostGIS geometry to GeoJSON"""
    shapely_point = to_shape(geometry)
    return GeoJSONPoint(type="Point", coordinates=[shapely_point.x, shapely_point.y])


def coords_to_wkt(latitude: float, longitude: float) -> str:
    """Convert latitude and longitude to WKT format"""
    return f"POINT({longitude} {latitude})"


def extract_coords(geometry) -> Tuple[float, float]:
    """Extract latitude and longitude from PostGIS geometry"""
    shapely_point = to_shape(geometry)
    return (shapely_point.y, shapely_point.x)


def utc_now():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def to_dict(obj: BaseModel) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary consistently,
    handling both old and new Pydantic versions.
    """
    if hasattr(obj, "model_dump"):
        # Pydantic v2
        return obj.model_dump()
    else:
        # Pydantic v1
        return obj.dict()


def to_dict_excluding_unset(obj: BaseModel) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary excluding unset fields,
    handling both old and new Pydantic versions.
    """
    if hasattr(obj, "model_dump"):
        # Pydantic v2
        return obj.model_dump(exclude_unset=True)
    else:
        # Pydantic v1
        return obj.dict(exclude_unset=True)
