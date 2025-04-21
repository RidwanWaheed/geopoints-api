def test_read_points(client, test_points):
    """Test getting all points."""
    response = client.get("/api/v1/points/")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "data" in data
    assert "meta" in data
    assert data["error"] is None

    # Check metadata
    assert data["meta"]["total"] > 0
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 20

    # Check data
    assert len(data["data"]) == len(test_points)


def test_read_point_by_id(client, test_points):
    """Test getting a specific point by ID."""
    # Get the first test point
    test_point = test_points[0]

    response = client.get(f"/api/v1/points/{test_point.id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_point.id
    assert data["name"] == test_point.name
    assert data["description"] == test_point.description
    assert "coordinates" in data
    assert data["coordinates"]["type"] == "Point"


def test_read_point_not_found(client):
    """Test getting a non-existent point."""
    response = client.get("/api/v1/points/999999")

    # Verify response
    assert response.status_code == 404
    data = response.json()

    # Check error message
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_create_point(client, test_categories, user_token):
    """Test creating a new point."""
    # Data for a new point
    point_data = {
        "name": "New Test Point",
        "description": "A point created during testing",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "category_id": test_categories[0].id,
    }

    # Send request with authentication
    response = client.post(
        "/api/v1/points/",
        json=point_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response
    assert response.status_code == 201
    data = response.json()

    # Check data
    assert data["name"] == point_data["name"]
    assert data["description"] == point_data["description"]
    assert data["coordinates"]["type"] == "Point"
    assert abs(data["coordinates"]["coordinates"][0] - point_data["longitude"]) < 1e-6
    assert abs(data["coordinates"]["coordinates"][1] - point_data["latitude"]) < 1e-6
    assert data["category_id"] == point_data["category_id"]


def test_create_point_unauthorized(client, test_categories):
    """Test creating a point without authentication."""
    # Data for a new point
    point_data = {
        "name": "Unauthorized Point",
        "description": "This point should not be created",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "category_id": test_categories[0].id,
    }

    # Send request without authentication
    response = client.post("/api/v1/points/", json=point_data)

    # Verify response
    assert response.status_code == 401


def test_update_point(client, test_points, user_token):
    """Test updating a point."""
    # Get the first test point
    test_point = test_points[0]

    # Data for updating the point
    update_data = {
        "name": "Updated Point Name",
        "description": "Updated description during testing",
    }

    # Send request with authentication
    response = client.put(
        f"/api/v1/points/{test_point.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_point.id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_point(client, test_points, admin_token):
    """Test deleting a point (requires admin rights)."""
    # Get the first test point
    test_point = test_points[0]

    # Delete the point
    response = client.delete(
        f"/api/v1/points/{test_point.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_point.id

    # Verify the point is no longer accessible
    response = client.get(f"/api/v1/points/{test_point.id}")
    assert response.status_code == 404


def test_delete_point_not_admin(client, test_points, user_token):
    """Test that a regular user cannot delete a point."""
    # Get the first test point
    test_point = test_points[0]

    # Try to delete the point with a regular user token
    response = client.delete(
        f"/api/v1/points/{test_point.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response
    assert response.status_code == 403


def test_nearby_points(client, test_points):
    """Test getting points near a location."""
    # Test getting points near Brandenburg Gate
    lat, lng = 52.5163, 13.3777  # Brandenburg Gate

    # Rather than expecting exact counts, just validate that smaller radiuses return fewer points
    response_small = client.get(f"/api/v1/points/nearby?lat={lat}&lng={lng}&radius=500")
    response_large = client.get(
        f"/api/v1/points/nearby?lat={lat}&lng={lng}&radius=5000"
    )

    # Verify responses
    assert response_small.status_code == 200
    assert response_large.status_code == 200

    small_data = response_small.json()
    large_data = response_large.json()

    # Should have points in both responses
    assert len(small_data) > 0
    assert len(large_data) > 0

    # Larger radius should return more or equal points
    assert len(large_data) >= len(small_data)


def test_nearest_points(client, test_points):
    """Test getting nearest points to a location."""
    # Test getting points near Berlin center
    lat, lng = 52.5200, 13.4050

    # Test getting the 3 nearest points
    response = client.get(f"/api/v1/points/nearest?lat={lat}&lng={lng}&limit=3")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check result count
    assert len(data) == 3

    # Verify all results have a distance field
    for point in data:
        assert "distance" in point

    # Results should be ordered by distance
    distances = [point["distance"] for point in data]
    assert distances == sorted(distances), "Results are not ordered by distance"


def test_within_polygon(client, test_points):
    """Test finding points within a polygon."""
    # Create a WKT polygon covering central Berlin
    polygon_wkt = "POLYGON((13.3 52.5, 13.3 52.55, 13.45 52.55, 13.45 52.5, 13.3 52.5))"

    # Make API request
    response = client.post(f"/api/v1/points/within?polygon_wkt={polygon_wkt}")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # We should have some points in the result
    assert len(data) > 0

    # Points should have coordinates
    for point in data:
        assert "coordinates" in point
        assert point["coordinates"]["type"] == "Point"


def test_filter_points_by_category(client, test_points, test_categories):
    """Test filtering points by category."""
    # Get category id with most points (Park)
    park_category_id = test_categories[2].id

    # Count how many test points have this category
    expected_count = sum(1 for p in test_points if p.category_id == park_category_id)

    # Make request with category filter
    response = client.get(f"/api/v1/points/?category_id={park_category_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "data" in data
    assert "meta" in data

    # Check data count
    assert data["meta"]["total"] == expected_count
    assert len(data["data"]) == expected_count

    # All returned points should have the requested category
    for point in data["data"]:
        assert point["category_id"] == park_category_id
