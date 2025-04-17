import logging
from typing import Any, Dict, Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI app"""

    @app.exception_handler(BaseAPIException)
    async def handle_base_api_exception(
        request: Request, exc: BaseAPIException
    ) -> JSONResponse:
        """Handle custom API exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors from pydantic models"""
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_exception(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle database errors"""
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Database operation failed"},
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
    
    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors from pydantic models"""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": errors,
            },
        )
