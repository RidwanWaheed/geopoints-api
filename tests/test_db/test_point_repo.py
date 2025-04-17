import pytest
from geoalchemy2.shape import to_shape
from sqlalchemy import func
from shapely import wkt
from shapely.geometry import Point as ShapelyPoint

from app.repositories.point import PointRepository
from app.schemas.point import PointCreate, PointUpdate


def test_create_from_coords(point_repository, db_session, test_categories):
    """Test creating a point from coordinates."""
    # Create point data
    point_data = PointCreate(
        name="Test Point",
        description="A test point",
        latitude=52.5200,
        longitude=13.4050,
        category_id=test_categories[0].id
    )
    
    # Create the point
    point = point_repository.create_from_coords(obj_in=point_data)
    
    # Verify point data
    assert point.id is not None
    assert point.name == point_data.name
    assert point.description == point_data.description
    assert point.category_id == point_data.category_id
    
    # Verify geometry
    assert point.geometry is not None
    shapely_point = to_shape(point.geometry)
    assert abs(shapely_point.x - point_data.longitude) < 1e-6
    assert abs(shapely_point.y - point_data.latitude) < 1e-6


def test_get_point(point_repository, test_points):
    """Test getting a point by ID."""
    # Get the first test point
    test_point = test_points[0]
    
    # Get the point from the repository
    point = point_repository.get(id=test_point.id)
    
    # Verify point data
    assert point is not None
    assert point.id == test_point.id
    assert point.name == test_point.name
    assert point.description == test_point.description
    assert point.category_id == test_point.category_id


def test_get_nonexistent_point(point_repository):
    """Test getting a nonexistent point."""
    point = point_repository.get(id=999999)
    assert point is None


def test_get_points(point_repository, test_points):
    """Test getting multiple points."""
    # Get all points
    points = point_repository.get_multi()
    
    # Verify we get all test points
    assert len(points) == len(test_points)


def test_get_points_with_limit(point_repository, test_points):
    """Test getting points with limit."""
    # Get 2 points
    points = point_repository.get_multi(limit=2)
    
    # Verify we get exactly 2 points
    assert len(points) == 2


def test_get_points_with_skip(point_repository, test_points):
    """Test getting points with skip."""
    # Get all points, skipping the first one
    points = point_repository.get_multi(skip=1)
    
    # Verify we get one less than the total
    assert len(points) == len(test_points) - 1


def test_get_by_category(point_repository, test_points, test_categories):
    """Test getting points by category."""
    # Get category ID with most points (Park)
    park_category_id = test_categories[2].id
    
    # Count how many test points have this category
    expected_count = sum(1 for p in test_points if p.category_id == park_category_id)
    
    # Get points by category
    points = point_repository.get_by_category(category_id=park_category_id)
    
    # Verify we get the expected number of points
    assert len(points) == expected_count
    
    # All points should have the requested category
    for point in points:
        assert point.category_id == park_category_id


def test_update_point(point_repository, test_points):
    """Test updating a point."""
    # Get the first test point
    test_point = test_points[0]
    
    # Create update data
    update_data = PointUpdate(
        name="Updated Point",
        description="An updated point description"
    )
    
    # Update the point
    updated_point = point_repository.update(db_obj=test_point, obj_in=update_data)
    
    # Verify point data
    assert updated_point.id == test_point.id
    assert updated_point.name == update_data.name
    assert updated_point.description == update_data.description
    
    # Other fields should remain unchanged
    assert updated_point.category_id == test_point.category_id
    assert updated_point.geometry == test_point.geometry


def test_update_point_coordinates(point_repository, test_points):
    """Test updating a point's coordinates."""
    # Get the first test point
    test_point = test_points[0]
    
    # Create update data with new coordinates
    update_data = PointUpdate(
        latitude=52.5200,
        longitude=13.4050
    )
    
    # Update the point
    updated_point = point_repository.update(db_obj=test_point, obj_in=update_data)
    
    # Verify coordinates were updated
    shapely_point = to_shape(updated_point.geometry)
    assert abs(shapely_point.x - update_data.longitude) < 0.1
    assert abs(shapely_point.y - update_data.latitude) < 0.1


def test_remove_point(point_repository, test_points):
    """Test removing a point."""
    # Get the first test point
    test_point = test_points[0]
    
    # Remove the point
    removed_point = point_repository.remove(id=test_point.id)
    
    # Verify removed point data
    assert removed_point.id == test_point.id
    
    # The point should no longer exist in the database
    point = point_repository.get(id=test_point.id)
    assert point is None


def test_count_points(point_repository, test_points):
    """Test counting points."""
    # Count all points
    count = point_repository.count()
    
    # Verify we get the expected count
    assert count == len(test_points)


def test_count_points_by_category(point_repository, test_points, test_categories):
    """Test counting points by category."""
    # Get category ID with most points (Park)
    park_category_id = test_categories[2].id
    
    # Count how many test points have this category
    expected_count = sum(1 for p in test_points if p.category_id == park_category_id)
    
    # Count points by category
    count = point_repository.count(category_id=park_category_id)
    
    # Verify we get the expected count
    assert count == expected_count


def test_get_nearby(point_repository, test_points):
    """Test getting nearby points."""
    # Test getting points near Brandenburg Gate
    lat, lng = 52.5163, 13.3777  # Brandenburg Gate
    
    # Get points within 2km
    nearby_points = point_repository.get_nearby(lat=lat, lng=lng, radius=2050)
    
    # Verify we get points with distances
    assert len(nearby_points) >= 2
    
    for point, distance in nearby_points:
        # Points should have distance information
        assert distance is not None
        assert distance >= 0


def test_get_nearest(point_repository, test_points):
    """Test getting nearest points."""
    # Test getting points near Berlin center
    lat, lng = 52.5200, 13.4050
    
    # Get 3 nearest points
    nearest_points = point_repository.get_nearest(lat=lat, lng=lng, limit=3)
    
    # Verify we get points with distances
    assert len(nearest_points) == 3
    for point, distance in nearest_points:
        assert distance >= 0
    
    # Verify points are ordered by distance
    distances = [distance for _, distance in nearest_points]
    assert distances == sorted(distances)


def test_get_within_polygon(point_repository, test_points):
    """Test getting points within a polygon."""
    # Define a polygon covering central Berlin
    polygon_wkt = "POLYGON((13.3 52.5, 13.3 52.55, 13.45 52.55, 13.45 52.5, 13.3 52.5))"
    
    # Get points within the polygon
    points = point_repository.get_within_polygon(polygon=polygon_wkt)
    
    # Parse the WKT into a shapely polygon
    polygon = wkt.loads(polygon_wkt)
    
    # Count points manually
    manual_count = 0
    for point in test_points:
        shapely_point = to_shape(point.geometry)
        if polygon.contains(ShapelyPoint(shapely_point.x, shapely_point.y)):
            manual_count += 1
    
    # Verify we get the expected count
    assert len(points) == manual_count