from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_category_service,
    get_current_active_user,
    get_current_superuser,
)
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.pagination import PagedResponse, PageParams
from app.services.category import CategoryService

router = APIRouter()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    """Create a new category (requires superuser privileges)"""
    return service.create(obj_in=category_in)


@router.get("/", response_model=PagedResponse[Category])
def read_categories(
    *,
    pagination: PageParams = Depends(),
    service: CategoryService = Depends(get_category_service),
):
    """Retrieve categories with pagination"""
    # Get total count
    total = service.count()

    # Get paginated items
    items = service.get_multi(
        skip=(pagination.page - 1) * pagination.limit, limit=pagination.limit
    )

    # Return paginated response
    return PagedResponse.create(
        items=items, total=total, page=pagination.page, limit=pagination.limit
    )


@router.get("/{category_id}", response_model=Category)
def read_category(
    *, category_id: int, service: CategoryService = Depends(get_category_service)
):
    """Get a specific category by id"""
    category = service.get(id=category_id)
    if not category:
        raise NotFoundException(detail=f"Category with id {category_id} not found")
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    """Update a category (requires superuser privileges)"""
    updated_category = service.update(id=category_id, obj_in=category_in)
    if not updated_category:
        raise NotFoundException(detail=f"Category with id {category_id} not found")
    return updated_category


@router.delete("/{category_id}", response_model=Category)
def delete_category(
    *,
    category_id: int,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    """Delete a category (requires superuser privileges)"""
    category = service.get(id=category_id)
    if not category:
        raise NotFoundException(detail=f"Category with id {category_id} not found")
    return service.remove(id=category_id)
