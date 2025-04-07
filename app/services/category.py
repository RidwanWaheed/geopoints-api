from sqlalchemy import func
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        """Create a new category"""
        return self.repository.create(db=db, obj_in=obj_in)
    
    def get(self, db: Session, *, id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.repository.get(db=db, id=id)
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        """Get category by name"""
        return self.repository.get_by_name(db=db, name=name)
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get multiple categories"""
        return self.repository.get_multi(db=db, skip=skip, limit=limit)

    def update(self, db: Session, *, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        """Update a category"""
        return self.repository.update(db=db, db_obj=db_obj, obj_in=obj_in)
    
    def remove(self, db: Session, *, id: int) -> Category:
         """Remove a category"""
         return self.repository.remove(db=db, id=id)
    
    def count(self, db: Session) -> int:
        """Count total categories"""
        return db.query(func.count(Category.id)).scalar()
