from fastapi import APIRouter

from app.api.endpoints import points, categories, test

api_router = APIRouter()
# api_router.include_router(points.router, prefix="/points", tags=["points"])
# api_router.include_router(categories.router, prefix="/categories", tags=["categories"])

api_router.include_router(test.router, prefix="/test", tags=["test"])