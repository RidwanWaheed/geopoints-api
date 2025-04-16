from typing import Tuple
from datetime import datetime, timezone

from geoalchemy2.shape import to_shape
from geojson_pydantic import Point as GeoJSONPoint


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
