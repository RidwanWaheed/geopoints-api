from fastapi import Query
from geoalchemy2 import WKBElement
import pytest
import math
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point as ShapelyPoint, Polygon
from sqlalchemy import func
from app.models.point import Point

from app.spatial.queries import (
    point_to_ewkb, 
    add_distance_to_query, 
    filter_by_distance,
    nearest_neighbor_query
)
from app.core.constants import SpatialRefSys


def test_point_to_ewkb(db_session):
    """Test conversion of lat/lng to PostGIS EWKB format."""
    # Test point in Berlin
    lat, lng = 52.5200, 13.4050
    
    # Convert to EWKB
    ewkb_point = point_to_ewkb(lat, lng)
    
    # Make sure we can convert it back 
    shapely_point = to_shape(ewkb_point)
    
    # Verify coordinates (with a small epsilon for floating point comparison)
    assert abs(shapely_point.x - lng) < 1e-6
    assert abs(shapely_point.y - lat) < 1e-6
    
    # Verify SRID
    assert ewkb_point.srid == SpatialRefSys.WGS84


def test_add_distance_to_query(db_session, test_points):
    """Test adding distance calculation to query."""
    # Test point near Berlin center
    lat, lng = 52.5200, 13.4050
    point_geom = point_to_ewkb(lat, lng)
    
    # Create base query
    query = db_session.query(Point)
    
    # Add distance calculation
    query_with_distance = add_distance_to_query(query, Point, point_geom)
    
    # Execute query and get results
    results = query_with_distance.all()
    
    # We should have as many results as test points
    assert len(results) == len(test_points)
    
    # Each result should be a tuple of (Point, distance)
    for result in results:
        assert len(result) == 2
        assert isinstance(result[0], Point)
        assert isinstance(result[1], float)
        
        # Distance should be positive
        assert result[1] >= 0


def filter_by_distance(query: Query, model_class, point_geom: WKBElement, radius: float) -> Query:
    """
    Filter a query by distance using an explicit distance condition
    
    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        point_geom: Source geometry to measure distance from
        radius: Distance in meters

    Returns:
        Filtered query
    """
    # Add an explicit filter on the distance column
    # This is more reliable than ST_DWithin which can sometimes include points outside the radius
    return query.having(func.ST_Distance(
        func.geography(model_class.geometry), 
        func.geography(point_geom)
    ) <= radius)


def test_nearest_neighbor_query(db_session, test_points):
    """Test nearest neighbor query optimized with KNN."""
    # Test point near Berlin center
    lat, lng = 52.5200, 13.4050
    point_geom = point_to_ewkb(lat, lng)
    
    # Create base query
    query = db_session.query(Point)
    
    # Add distance calculation
    query = add_distance_to_query(query, Point, point_geom)
    
    # Optimize for nearest neighbor
    query = nearest_neighbor_query(query, Point, point_geom)
    
    # Get the top 3 nearest points
    query = query.limit(3)
    
    # Execute query and get results
    results = query.all()
    
    # Should have 3 results
    assert len(results) == 3
    
    # Results should be in order of distance (closest first)
    distances = [distance for _, distance in results]
    assert distances == sorted(distances), "Results are not ordered by distance"
    
    # Check that we have the expected nearest point
    nearest_point, nearest_distance = results[0]
    
    # Calculate Haversine distance manually to verify
    def haversine(lat1, lon1, lat2, lon2):
        # Convert decimal degrees to radians 
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371000  # Radius of earth in meters
        return c * r
    
    # Get coordinates of nearest point
    shapely_point = to_shape(nearest_point.geometry)
    point_lat, point_lng = shapely_point.y, shapely_point.x
    
    # Haversine distance should be close to the calculated distance
    haversine_distance = haversine(lat, lng, point_lat, point_lng)
    assert abs(nearest_distance - haversine_distance) < 10, "Distance calculation is significantly different from Haversine"


def test_points_within_polygon(db_session, test_points):
    """Test finding points within a polygon."""
    
    # Create a polygon covering central Berlin
    polygon = Polygon([
        (13.3, 52.5),       # Southwest corner
        (13.3, 52.55),      # Northwest corner
        (13.45, 52.55),     # Northeast corner
        (13.45, 52.5),      # Southeast corner
        (13.3, 52.5)        # Close the polygon
    ])
    
    # Convert to WKT
    polygon_wkt = f"POLYGON(({', '.join([f'{x} {y}' for x, y in polygon.exterior.coords])}))"
    
    # Use raw SQL with ST_Within to find points in the polygon
    query = db_session.query(Point).filter(
        func.ST_Within(
            Point.geometry,
            func.ST_GeomFromText(polygon_wkt, SpatialRefSys.WGS84)
        )
    )
    
    # Execute query
    points_in_polygon = query.all()
    
    # Count points within the polygon manually for verification
    manual_count = 0
    for point in test_points:
        shapely_point = to_shape(point.geometry)
        if polygon.contains(ShapelyPoint(shapely_point.x, shapely_point.y)):
            manual_count += 1
    
    # The query count should match our manual count
    assert len(points_in_polygon) == manual_count