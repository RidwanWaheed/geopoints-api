from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    """Repository for Category entities"""

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.session.query(Category).filter(Category.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get multiple categories with pagination"""
        return self.session.query(Category).offset(skip).limit(limit).all()

    def create(self, *, obj_data: Dict[str, Any]) -> Category:
        """Create a new category"""
        db_obj = Category(**obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: Category, obj_data: Dict[str, Any]) -> Category:
        """Update a category"""
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, *, id: int) -> Optional[Category]:
        """Delete a category"""
        obj = self.get(id=id)
        if not obj:
            return None

        self.session.delete(obj)
        self.session.commit()
        return obj

    def get_by_name(self, *, name: str) -> Optional[Category]:
        """Get a category by name"""
        return self.session.query(Category).filter(Category.name == name).first()

    def name_exists(self, *, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a category name already exists (for validation)"""
        query = self.session.query(Category).filter(Category.name == name)
        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)
        return self.session.query(query.exists()).scalar()

    def count(self) -> int:
        """Count total categories"""
        return self.session.query(func.count(Category.id)).scalar()
