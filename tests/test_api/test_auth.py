def test_login_success(client, test_users):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "Admin123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check token structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_wrong_password(client, test_users):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "WrongPassword123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Verify response
    assert response.status_code == 401
    data = response.json()

    # Check error message
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent@example.com", "password": "AnyPassword123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Verify response
    assert response.status_code == 401
    data = response.json()

    # Check error message
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()


def test_login_inactive_user(client, test_users):
    """Test login with inactive user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "inactive@example.com", "password": "Inactive123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Verify response - should be unauthorized
    assert response.status_code == 401


def test_register_user(client):
    """Test registering a new user."""
    # Data for a new user
    user_data = {
        "email": "newuser@example.com",
        "username": "new_test_user",
        "password": "NewUser123!",
        "is_active": True,
        "is_superuser": False,
    }

    # Register the user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Verify response
    assert response.status_code == 201
    data = response.json()

    # Check user data
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "created_at" in data

    # Password should not be in the response
    assert "password" not in data
    assert "hashed_password" not in data

    # Now try to login with the new user
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": user_data["email"], "password": user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Verify successful login
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_register_user_duplicate_email(client, test_users):
    """Test registration with an email that already exists."""
    # Data for a new user with existing email
    user_data = {
        "email": "admin@example.com",  # This email already exists
        "username": "different_username",
        "password": "DiffUser123!",
        "is_active": True,
        "is_superuser": False,
    }

    # Try to register the user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Verify response
    assert response.status_code == 400


def test_register_user_duplicate_username(client, test_users):
    """Test registration with a username that already exists."""
    # Data for a new user with existing username
    user_data = {
        "email": "different@example.com",
        "username": "admin",  # This username already exists
        "password": "DiffUser123!",
        "is_active": True,
        "is_superuser": False,
    }

    # Try to register the user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Verify response
    assert response.status_code == 400


def test_get_current_user(client, user_token):
    """Test getting the current user information."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Check user data
    assert "id" in data
    assert "email" in data
    assert data["email"] == "user@example.com"
    assert data["username"] == "regular_user"
    assert data["is_active"] is True
    assert data["is_superuser"] is False


def test_get_current_user_no_token(client):
    """Test that getting current user fails without a token."""
    response = client.get("/api/v1/auth/me")

    # Verify response
    assert response.status_code == 401


def test_logout(client, user_token):
    """Test logging out a user."""
    # First make a request that should work with the token
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

    # Now logout
    logout_response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {user_token}"}
    )

    # Verify logout response
    assert logout_response.status_code == 200
    assert "message" in logout_response.json()

    # The token should now be invalidated, so the request should fail
    response_after_logout = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response_after_logout.status_code == 401
