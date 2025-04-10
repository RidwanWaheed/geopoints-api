from geoalchemy2.shape import to_shape
from shapely.geometry import Point as ShapelyPoint
from geojson_pydantic import Point as GeoJSONPoint
from typing import Tuple

def point_to_geojson(geometry) -> GeoJSONPoint:
    """Convert PostGIS geometry to GeoJSON"""
    shapely_point = to_shape(geometry)
    return GeoJSONPoint(coordinates=[shapely_point.x, shapely_point.y])

def coords_to_wkt(latitude: float, longitude: float) -> str:
    """Convert latitude and longitude to WKT format"""
    return f"POINT({longitude} {latitude})"

def extract_coords(geometry) -> Tuple[float, float]:
    """Extract latitude and longitude from PostGIS geometry"""
    shapely_point = to_shape(geometry)
    return (shapely_point.y, shapely_point.x)  # (latitude, longitude)

