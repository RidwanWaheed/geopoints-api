from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PageParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(
        1, ge=1, description="Page number (1-indexed)", json_schema_extra={"example": 1}
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Items per page (max 100)",
        json_schema_extra={"example": 20},
    )

    @field_validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than or equal to 1")
        return v

    @field_validator("limit")
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError("Limit must be greater than or equal to 1")
        if v > 100:
            raise ValueError("Limit must be less than or equal to 100")
        return v


class PageMetadata(BaseModel):
    """Pagination metadata"""

    total: int = Field(
        ..., description="Total number of items", json_schema_extra={"example": 42}
    )
    page: int = Field(
        ..., description="Current page number", json_schema_extra={"example": 1}
    )
    limit: int = Field(
        ..., description="Items per page", json_schema_extra={"example": 20}
    )
    pages: int = Field(
        ..., description="Total number of pages", json_schema_extra={"example": 3}
    )


class PagedResponse(BaseModel, Generic[T]):
    """Generic response with pagination"""

    data: List[T] = Field(..., description="Data items")
    meta: PageMetadata = Field(..., description="Pagination metadata")
    error: Optional[str] = Field(None, description="Error message")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        """Create a paged response"""
        pages = (total + limit - 1) // limit if limit > 0 else 0
        meta = PageMetadata(total=total, page=page, limit=limit, pages=pages)
        return cls(data=items, meta=meta)
