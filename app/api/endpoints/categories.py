from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import get_db
from app.api.deps import get_category_service
from app.services.category import CategoryService
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
):
    """Create a new category"""
    return service.create(db=db, obj_in=category_in)

@router.get("/", response_model=List[Category])
def read_categories(
    *,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
):
    """Retrieve categories"""
    return service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=Category)
def read_category(
    *,
    category_id: int,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
):
    """Get a specific category by id"""
    category = service.get(db=db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return Category    

@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
):
     """Update a category"""
     category = service.get(db=db, id=category_id)
     if not category:
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Category not found"
         )
     return service.update(db=db, db_obj=category, obj_in=category_in)

@router.delete("/{category_id}", response_model=Category)
def delete_category(
    *,
    category_id: int,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
):
    """Delete a category"""
    category = service.get(db=db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return service.remove(db=db, id=category_id)
