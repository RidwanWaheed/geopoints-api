from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.base import BaseRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Category)

    def get_by_name(self, *, name: str) -> Optional[Category]:
        """Get category by name"""
        return self.session.session.query(Category).filter(Category.name == name).first()
    
    def count(self) -> int:
        """Count total categories"""
        return self.session.query(func.count(Category.id)).scalar()