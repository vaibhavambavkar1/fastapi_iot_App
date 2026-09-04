from typing import Any


class AppError(Exception):
    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str, details: Any | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


class BusinessValidationError(AppError):
    status_code = 422
    error_code = "business_validation_error"
