def test_read_categories(client, test_categories):
    """Test getting all categories."""
    response = client.get("/api/v1/categories/")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "data" in data
    assert "meta" in data
    assert data["error"] is None

    # Check metadata
    assert data["meta"]["total"] == len(test_categories)
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 20

    # Check data
    assert len(data["data"]) == len(test_categories)

    # Verify category fields
    for category in data["data"]:
        assert "id" in category
        assert "name" in category
        assert "description" in category
        assert "color" in category


def test_read_category_by_id(client, test_categories):
    """Test getting a specific category by ID."""
    # Get the first test category
    test_category = test_categories[0]

    response = client.get(f"/api/v1/categories/{test_category.id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_category.id
    assert data["name"] == test_category.name
    assert data["description"] == test_category.description
    assert data["color"] == test_category.color


def test_read_category_not_found(client):
    """Test getting a non-existent category."""
    response = client.get("/api/v1/categories/999999")

    # Verify response
    assert response.status_code == 404
    data = response.json()

    # Check error message
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_create_category(client, admin_token):
    """Test creating a new category (requires admin rights)."""
    # Data for a new category
    category_data = {
        "name": "Nightlife",
        "description": "Bars, clubs and nightlife venues",
        "color": "#9932CC",
    }

    # Send request with admin authentication
    response = client.post(
        "/api/v1/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == 201
    data = response.json()

    # Check data
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert data["color"] == category_data["color"]
    assert "id" in data


def test_create_category_unauthorized(client):
    """Test creating a category without authentication."""
    # Data for a new category
    category_data = {
        "name": "Unauthorized Category",
        "description": "This category should not be created",
        "color": "#FF0000",
    }

    # Send request without authentication
    response = client.post("/api/v1/categories/", json=category_data)

    # Verify response
    assert response.status_code == 401


def test_create_category_not_admin(client, user_token):
    """Test that a regular user cannot create a category."""
    # Data for a new category
    category_data = {
        "name": "Regular User Category",
        "description": "This category should not be created",
        "color": "#00FF00",
    }

    # Send request with regular user authentication
    response = client.post(
        "/api/v1/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response - should be forbidden
    assert response.status_code == 403


def test_update_category(client, test_categories, admin_token):
    """Test updating a category (requires admin rights)."""
    # Get the first test category
    test_category = test_categories[0]

    # Data for updating the category
    update_data = {
        "name": "Updated Category Name",
        "description": "Updated description during testing",
        "color": "#0000FF",
    }

    # Send request with admin authentication
    response = client.put(
        f"/api/v1/categories/{test_category.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_category.id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["color"] == update_data["color"]


def test_update_category_not_admin(client, test_categories, user_token):
    """Test that a regular user cannot update a category."""
    # Get the first test category
    test_category = test_categories[0]

    # Data for updating the category
    update_data = {
        "name": "Regular User Update",
        "description": "This update should be rejected",
    }

    # Send request with regular user authentication
    response = client.put(
        f"/api/v1/categories/{test_category.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response - should be forbidden
    assert response.status_code == 403


def test_delete_category(client, test_categories, admin_token):
    """Test deleting a category (requires admin rights)."""
    # Get the first test category
    test_category = test_categories[0]

    # Delete the category
    response = client.delete(
        f"/api/v1/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check data
    assert data["id"] == test_category.id

    # Verify the category is no longer accessible
    response = client.get(f"/api/v1/categories/{test_category.id}")
    assert response.status_code == 404


def test_delete_category_not_admin(client, test_categories, user_token):
    """Test that a regular user cannot delete a category."""
    # Get the first test category
    test_category = test_categories[0]

    # Try to delete the category with a regular user token
    response = client.delete(
        f"/api/v1/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify response - should be forbidden
    assert response.status_code == 403
