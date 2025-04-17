import pytest
import sqlalchemy
from sqlalchemy.exc import IntegrityError

from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


def test_create_category(category_repository, db_session):
    """Test creating a category."""
    # Create category data
    category_data = CategoryCreate(
        name="Test Category",
        description="A test category",
        color="#FF5733"
    )
    
    # Create the category
    category = category_repository.create(obj_in=category_data)
    
    # Verify category data
    assert category.id is not None
    assert category.name == category_data.name
    assert category.description == category_data.description
    assert category.color == category_data.color


def test_create_category_duplicate_name(category_repository, db_session):
    """Test creating a category with a duplicate name."""
    # First, create a category that we'll attempt to duplicate
    initial_category = CategoryCreate(
        name="DuplicateTest",
        description="Original category",
        color="#AABBCC"
    )
    
    # Create the initial category
    category = category_repository.create(obj_in=initial_category)
    db_session.commit()
    
    # Now try to create a duplicate
    duplicate_category = CategoryCreate(
        name="DuplicateTest",
        description="This should fail",
        color="#FF0000"
    )
    
    try:
        category = category_repository.create(obj_in=duplicate_category)
        db_session.flush()
        
        # If we get here, the duplicate was somehow allowed - fail the test
        assert False, "Database allowed duplicate category name"
    except sqlalchemy.exc.IntegrityError:
        # This is what we expect - a constraint violation
        db_session.rollback()
    except Exception as e:
        # Other exceptions should also be handled but will fail the test
        db_session.rollback()
        assert False, f"Unexpected exception: {str(e)}"


def test_get_category(category_repository, test_categories):
    """Test getting a category by ID."""
    # Get the first test category
    test_category = test_categories[0]
    
    # Get the category from the repository
    category = category_repository.get(id=test_category.id)
    
    # Verify category data
    assert category is not None
    assert category.id == test_category.id
    assert category.name == test_category.name
    assert category.description == test_category.description
    assert category.color == test_category.color


def test_get_nonexistent_category(category_repository):
    """Test getting a nonexistent category."""
    category = category_repository.get(id=999999)
    assert category is None


def test_get_categories(category_repository, test_categories):
    """Test getting multiple categories."""
    # Get all categories
    categories = category_repository.get_multi()
    
    # Verify we get all test categories
    assert len(categories) == len(test_categories)


def test_get_categories_with_limit(category_repository, test_categories):
    """Test getting categories with limit."""
    # Get 2 categories
    categories = category_repository.get_multi(limit=2)
    
    # Verify we get exactly 2 categories
    assert len(categories) == 2


def test_get_categories_with_skip(category_repository, test_categories):
    """Test getting categories with skip."""
    # Get all categories, skipping the first one
    categories = category_repository.get_multi(skip=1)
    
    # Verify we get one less than the total
    assert len(categories) == len(test_categories) - 1


def test_get_category_by_name(category_repository, test_categories):
    """Test getting a category by name."""
    # Get the first test category
    test_category = test_categories[0]
    
    # Get the category from the repository by name
    category = category_repository.get_by_name(name=test_category.name)
    
    # Verify category data
    assert category is not None
    assert category.id == test_category.id
    assert category.name == test_category.name


def test_get_nonexistent_category_by_name(category_repository):
    """Test getting a nonexistent category by name."""
    category = category_repository.get_by_name(name="Nonexistent Category")
    assert category is None


def test_update_category(category_repository, test_categories):
    """Test updating a category."""
    # Get the first test category
    test_category = test_categories[0]
    
    # Create update data
    update_data = CategoryUpdate(
        name="Updated Category",
        description="An updated category description",
        color="#00FF00"
    )
    
    # Update the category
    updated_category = category_repository.update(db_obj=test_category, obj_in=update_data)
    
    # Verify category data
    assert updated_category.id == test_category.id
    assert updated_category.name == update_data.name
    assert updated_category.description == update_data.description
    assert updated_category.color == update_data.color


def test_update_category_partial(category_repository, test_categories):
    """Test partially updating a category."""
    # Get the first test category
    test_category = test_categories[0]
    original_name = test_category.name
    
    # Create update data with only description
    update_data = CategoryUpdate(
        description="Updated description only"
    )
    
    # Update the category
    updated_category = category_repository.update(db_obj=test_category, obj_in=update_data)
    
    # Verify category data - name should remain unchanged
    assert updated_category.id == test_category.id
    assert updated_category.name == original_name
    assert updated_category.description == update_data.description
    assert updated_category.color == test_category.color


def test_update_category_dict(category_repository, test_categories):
    """Test updating a category with a dictionary."""
    # Get the first test category
    test_category = test_categories[0]
    
    # Create update data as a dictionary
    update_data = {
        "name": "Dict Updated Category",
        "color": "#0000FF"
    }
    
    # Update the category
    updated_category = category_repository.update(db_obj=test_category, obj_in=update_data)
    
    # Verify category data
    assert updated_category.id == test_category.id
    assert updated_category.name == update_data["name"]
    assert updated_category.description == test_category.description  # Unchanged
    assert updated_category.color == update_data["color"]


def test_remove_category(category_repository, test_categories):
    """Test removing a category."""
    # Get the first test category
    test_category = test_categories[0]
    
    # Remove the category
    removed_category = category_repository.remove(id=test_category.id)
    
    # Verify removed category data
    assert removed_category.id == test_category.id
    
    # The category should no longer exist in the database
    category = category_repository.get(id=test_category.id)
    assert category is None


def test_count_categories(category_repository, test_categories):
    """Test counting categories."""
    # Count all categories
    count = category_repository.count()
    
    # Verify we get the expected count
    assert count == len(test_categories)