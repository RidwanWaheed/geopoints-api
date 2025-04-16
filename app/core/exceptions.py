from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base API exception with default status code and detail message"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self, detail=None, headers=None):
        if detail is not None:
            self.detail = detail
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )


class NotFoundException(BaseAPIException):
    """Resource not found exception"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class BadRequestException(BaseAPIException):
    """Bad request exception"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"


class DatabaseException(BaseAPIException):
    """Database operation exception"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Database operation failed"


class ValidationException(BaseAPIException):
    """Validation error exception"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"
