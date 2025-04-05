from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.category import Category
from app.repositories.base import Baserepository
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryRepository(Baserepository[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        """Get category by name"""
        return db.query(Category).filter(Category.name == name).first()
