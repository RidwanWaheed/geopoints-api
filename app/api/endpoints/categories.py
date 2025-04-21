from fastapi import APIRouter, Depends, Query, status

from app.api.deps import (
    get_category_service,
    get_current_superuser,
)
from app.models.user import User
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.pagination import PagedResponse, PageParams
from app.services.category import CategoryService

router = APIRouter()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(category_in=category_in)


@router.get("/", response_model=PagedResponse[Category])
def read_categories(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: CategoryService = Depends(get_category_service),
):
    page_params = PageParams(page=page, limit=limit)
    return service.get_categories(page_params=page_params)


@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int, service: CategoryService = Depends(get_category_service)
):
    return service.get_category(category_id=category_id)


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    return service.update_category(category_id=category_id, category_in=category_in)


@router.delete("/{category_id}", response_model=Category)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_superuser),
    service: CategoryService = Depends(get_category_service),
):
    return service.delete_category(category_id=category_id)
