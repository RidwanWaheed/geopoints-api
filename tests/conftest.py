import os
import sys

os.environ["TESTING"] = "true"
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_DB"] = "geopoints_test"
os.environ["SECRET_KEY"] = "test_secret_key_for_tests"

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

# Add project root to path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import app modules - IMPORTANT: import app directly, not from main
from app.base import Base
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.point import Point
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.point import PointRepository
from app.repositories.user import UserRepository
from main import app

env_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.test")
if os.path.exists(env_test_path):
    load_dotenv(env_test_path, override=False)

# Test database URL
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost/geopoints_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database and return an SQLAlchemy engine."""
    # Create test database if it doesn't exist
    engine = create_engine(TEST_DATABASE_URL)

    if database_exists(engine.url):
        # If database exists, drop it to start fresh
        drop_database(engine.url)

    create_database(engine.url)

    # Create PostGIS extension and tables using direct SQL
    with engine.connect() as conn:
        # Create PostGIS extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

        # Create users table
        conn.execute(
            text(
                """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                username VARCHAR(50) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP WITH TIME ZONE
            )
        """
            )
        )

        # Create categories table
        conn.execute(
            text(
                """
            CREATE TABLE categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                color VARCHAR(7),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create points table with PostGIS geometry
        conn.execute(
            text(
                """
            CREATE TABLE points (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                geometry GEOMETRY(Point, 4326) NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create spatial indexes
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_points_geometry ON points USING GIST (geometry)"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_points_name ON points USING btree (name)"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories USING btree (name)"
            )
        )

        conn.commit()

    yield engine

    # Teardown - drop test database
    if os.environ.get("TEST_KEEP_DB") != "1":
        drop_database(engine.url)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a fresh database session for a test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()

    # Create a session bound to the connection
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )
    db = TestingSessionLocal()

    try:
        yield db
    except Exception:
        # If there was an exception, make sure to rollback
        db.rollback()
        raise
    finally:
        # Always rollback at the end of the test
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with patched dependencies."""

    # Override the dependencies in the FastAPI app
    from app.api.deps import get_db

    # Store original dependencies
    original_dependencies = app.dependency_overrides.copy()

    # Override dependency to use our test session
    app.dependency_overrides[get_db] = lambda: db_session

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Restore original dependencies
    app.dependency_overrides = original_dependencies


@pytest.fixture(scope="function")
def point_repository(db_session):
    """Return a PointRepository instance with the test database session."""
    return PointRepository(db_session)


@pytest.fixture(scope="function")
def category_repository(db_session):
    """Return a CategoryRepository instance with the test database session."""
    return CategoryRepository(db_session)


@pytest.fixture(scope="function")
def user_repository(db_session):
    """Return a UserRepository instance with the test database session."""
    return UserRepository(db_session)


# Test data fixtures
@pytest.fixture(scope="function")
def test_categories(db_session):
    """Create test categories and return them."""
    # Clean up any existing data first
    db_session.execute(text("DELETE FROM points"))  # Delete points first
    db_session.execute(text("DELETE FROM categories"))
    db_session.commit()

    # Then create categories
    categories = [
        Category(name="Restaurant", description="Places to eat", color="#FF5733"),
        Category(name="Museum", description="Cultural venues", color="#33FF57"),
        Category(name="Park", description="Green spaces", color="#5733FF"),
    ]

    db_session.add_all(categories)
    db_session.commit()

    for category in categories:
        db_session.refresh(category)

    yield categories

    # Clean up points first to avoid FK constraints
    db_session.execute(text("DELETE FROM points"))
    db_session.execute(text("DELETE FROM categories"))
    db_session.commit()


@pytest.fixture(scope="function")
def test_points(db_session, test_categories):
    """Create test points and return them."""
    # Clean up any existing data first
    db_session.execute(text("DELETE FROM points"))
    db_session.commit()

    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point as ShapelyPoint

    points = [
        # Berlin tourist spots
        Point(
            name="Brandenburg Gate",
            description="Famous landmark in Berlin",
            geometry=from_shape(ShapelyPoint(13.3777, 52.5163), srid=4326),
            category_id=test_categories[2].id,  # Park
        ),
        Point(
            name="Berlin TV Tower",
            description="Iconic tower with observation deck",
            geometry=from_shape(ShapelyPoint(13.4094, 52.5208), srid=4326),
            category_id=test_categories[1].id,  # Museum
        ),
        Point(
            name="Checkpoint Charlie",
            description="Historic Cold War site",
            geometry=from_shape(ShapelyPoint(13.3904, 52.5077), srid=4326),
            category_id=test_categories[1].id,  # Museum
        ),
        Point(
            name="Tiergarten",
            description="Large park in central Berlin",
            geometry=from_shape(ShapelyPoint(13.3500, 52.5150), srid=4326),
            category_id=test_categories[2].id,  # Park
        ),
        Point(
            name="Burgermeister",
            description="Popular burger joint",
            geometry=from_shape(ShapelyPoint(13.4398, 52.5005), srid=4326),
            category_id=test_categories[0].id,  # Restaurant
        ),
    ]

    db_session.add_all(points)
    db_session.commit()

    for point in points:
        db_session.refresh(point)

    yield points

    # Clean up after test
    db_session.execute(text("DELETE FROM points"))
    db_session.commit()


@pytest.fixture(scope="function")
def test_users(db_session):
    """Create test users and return them."""
    # Clean up any existing data first
    db_session.execute(text("DELETE FROM users"))
    db_session.commit()

    users = [
        User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("Admin123!"),
            is_active=True,
            is_superuser=True,
        ),
        User(
            email="user@example.com",
            username="regular_user",
            hashed_password=get_password_hash("User123!"),
            is_active=True,
            is_superuser=False,
        ),
        User(
            email="inactive@example.com",
            username="inactive_user",
            hashed_password=get_password_hash("Inactive123!"),
            is_active=False,
            is_superuser=False,
        ),
    ]

    db_session.add_all(users)
    db_session.commit()

    for user in users:
        db_session.refresh(user)

    yield users

    # Clean up after test
    db_session.execute(text("DELETE FROM users"))
    db_session.commit()


@pytest.fixture(scope="function")
def admin_token(client, test_users):
    """Get an authentication token for the admin user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "Admin123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token_data = response.json()
    assert (
        "access_token" in token_data
    ), f"Failed to get admin token. Response: {response.text}"
    return token_data["access_token"]


@pytest.fixture(scope="function")
def user_token(client, test_users):
    """Get an authentication token for the regular user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "user@example.com", "password": "User123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token_data = response.json()
    assert (
        "access_token" in token_data
    ), f"Failed to get user token. Response: {response.text}"
    return token_data["access_token"]
