from typing import List, Optional

from app.mappers.category_mapper import CategoryMapper
from app.repositories.category import CategoryRepository
from app.schemas.category import Category as CategorySchema
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create(self, *, obj_in: CategoryCreate) -> CategorySchema:
        """Create a new category"""
        db_obj = self.repository.create(obj_in=obj_in)
        return CategoryMapper.to_schema(db_obj)

    def get(self, *, id: int) -> Optional[CategorySchema]:
        """Get category by ID"""
        db_obj = self.repository.get(id=id)
        return CategoryMapper.to_schema(db_obj)

    def get_by_name(self, *, name: str) -> Optional[CategorySchema]:
        """Get category by name"""
        db_obj = self.repository.get_by_name(name=name)
        return CategoryMapper.to_schema(db_obj)

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[CategorySchema]:
        """Get multiple categories"""
        db_objs = self.repository.get_multi(skip=skip, limit=limit)
        return CategoryMapper.to_schema_list(db_objs)

    def update(self, *, id: int, obj_in: CategoryUpdate) -> Optional[CategorySchema]:
        """Update a category"""
        db_obj = self.repository.get(id=id)
        if not db_obj:
            return None

        updated_obj = self.repository.update(db_obj=db_obj, obj_in=obj_in)
        return CategoryMapper.to_schema(updated_obj)

    def remove(self, *, id: int) -> CategorySchema:
        """Remove a category"""
        removed_obj = self.repository.remove(id=id)
        return CategoryMapper.to_schema(removed_obj)

    def count(self) -> int:
        """Count total categories"""
        return self.repository.count()
