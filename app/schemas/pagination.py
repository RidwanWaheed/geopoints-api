from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PageParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

class PageMetadata(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

class PagedResponse(BaseModel, Generic[T]):
    """Generic response with pagination"""
    data: List[T] = Field(..., description="Data items")
    meta: PageMetadata = Field(..., description="Pagination metadata")
    error: Optional[str] = Field(None, description="Error message")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        """Create a paged response"""
        pages = (total + limit - 1) // limit if limit > 0 else 0
        meta = PageMetadata(
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
        return cls(data=items, meta=meta)