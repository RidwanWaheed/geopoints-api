from typing import List

from app.models.category import Category
from app.schemas.category import Category as CategorySchema


class CategoryMapper:
    """
    Mapper class responsible for transforming between database models and API schemas
    for Category entities.
    """

    @staticmethod
    def to_schema(db_obj: Category) -> CategorySchema:
        """
        Convert a Category database model to a Category schema.
        """
        if not db_obj:
            return None

        return CategorySchema(
            id=db_obj.id,
            name=db_obj.name,
            description=db_obj.description,
            color=db_obj.color,
        )

    @staticmethod
    def to_schema_list(db_objs: List[Category]) -> List[CategorySchema]:
        """
        Convert a list of Category database models to a list of Category schemas.
        """
        return [CategoryMapper.to_schema(db_obj) for db_obj in db_objs]
