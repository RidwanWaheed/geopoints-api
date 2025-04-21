# app/services/category_service.py
from typing import List, Optional

from app.core.exceptions import BadRequestException, NotFoundException
from app.repositories.category import CategoryRepository
from app.schemas.category import Category as CategorySchema
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.pagination import PagedResponse, PageParams


class CategoryService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def create_category(self, *, category_in: CategoryCreate) -> CategorySchema:
        try:
            if self.category_repository.name_exists(name=category_in.name):
                raise BadRequestException(
                    detail=f"Category with name '{category_in.name}' already exists"
                )

            if category_in.color and not self._is_valid_hex_color(category_in.color):
                raise BadRequestException(
                    detail="Color must be a valid hex color code (e.g., #FF5733)"
                )

            category = self.category_repository.create(
                obj_data=category_in.model_dump()
            )

            self.category_repository.session.commit()
            self.category_repository.session.refresh(category)

            return self._category_to_schema(category)
        except Exception as e:
            self.category_repository.session.rollback()
            raise e

    def get_category(self, *, category_id: int) -> CategorySchema:
        category = self.category_repository.get(id=category_id)
        if not category:
            raise NotFoundException(detail=f"Category with ID {category_id} not found")

        return self._category_to_schema(category)

    def get_categories(
        self, *, page_params: PageParams
    ) -> PagedResponse[CategorySchema]:
        # Calculate pagination offset
        skip = (page_params.page - 1) * page_params.limit

        # Get total count and items
        total = self.category_repository.count()
        categories = self.category_repository.get_multi(
            skip=skip, limit=page_params.limit
        )

        # Transform to schemas
        category_schemas = [self._category_to_schema(c) for c in categories]

        # Create paginated response
        return PagedResponse.create(
            items=category_schemas,
            total=total,
            page=page_params.page,
            limit=page_params.limit,
        )

    def update_category(
        self, *, category_id: int, category_in: CategoryUpdate
    ) -> CategorySchema:
        try:
            category = self.category_repository.get(id=category_id)
            if not category:
                raise NotFoundException(
                    detail=f"Category with ID {category_id} not found"
                )

            if category_in.name and category_in.name != category.name:
                if self.category_repository.name_exists(
                    name=category_in.name, exclude_id=category_id
                ):
                    raise BadRequestException(
                        detail=f"Category with name '{category_in.name}' already exists"
                    )

            if category_in.color and not self._is_valid_hex_color(category_in.color):
                raise BadRequestException(
                    detail="Color must be a valid hex color code (e.g., #FF5733)"
                )

            update_data = category_in.model_dump(exclude_unset=True)
            category = self.category_repository.update(
                db_obj=category, obj_data=update_data
            )

            self.category_repository.session.commit()
            self.category_repository.session.refresh(category)

            return self._category_to_schema(category)
        except Exception as e:
            self.category_repository.session.rollback()
            raise e

    def delete_category(self, *, category_id: int) -> CategorySchema:
        try:
            category = self.category_repository.get(id=category_id)
            if not category:
                raise NotFoundException(
                    detail=f"Category with ID {category_id} not found"
                )

            category = self.category_repository.delete(id=category_id)

            self.category_repository.session.commit()

            return self._category_to_schema(category)
        except Exception as e:
            self.category_repository.session.rollback()
            raise e

    def _category_to_schema(self, category) -> CategorySchema:
        return CategorySchema(
            id=category.id,
            name=category.name,
            description=category.description,
            color=category.color,
        )

    def _is_valid_hex_color(self, color: str) -> bool:
        import re

        return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color))
