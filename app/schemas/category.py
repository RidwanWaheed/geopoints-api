from pydantic import BaseModel
from typing import Optional


# Shared properties
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

# Properties to receive on category creation
class CategoryCreate(CategoryBase):
    pass

# Properties to receive on category update
class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

# Properties shared by models stored in DB
class CategoryInDBBase(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True
    }

# Properties to return to client
class Category(CategoryInDBBase):
    pass