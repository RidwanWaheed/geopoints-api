# app/repositories/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.base import Base
from app.core.utils import to_dict, to_dict_excluding_unset

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get(self, id: int) -> Optional[ModelType]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        # Convert pydantic model to dict
        obj_in_data = to_dict(obj_in)
        # Create SQLAlchemy model instance
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(
        self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        # Handle case when obj_in is a dict
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Convert pydantic model to dict, excluding unset values
            update_data = to_dict_excluding_unset(obj_in)

        # Apply changes to model
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def remove(self, *, id: int) -> ModelType:
        obj = self.session.query(self.model).get(id)
        self.session.delete(obj)
        self.session.commit()
        return obj
