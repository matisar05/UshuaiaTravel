from rest_framework import status


class AppError(Exception):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "internal_error"
    message = "An unexpected error occurred"

    def __init__(self, message: str | None = None, code: str | None = None, http_status: int | None = None):
        self.message = message or self.message
        self.code = code or self.code
        self.http_status = http_status or self.http_status
        super().__init__(self.message)


class NotFoundError(AppError):
    http_status = status.HTTP_404_NOT_FOUND
    code = "not_found"

    def __init__(self, resource: str = "Resource", message: str | None = None):
        super().__init__(
            message=message or f"{resource} not found",
            code="not_found",
        )


class ValidationError(AppError):
    http_status = status.HTTP_400_BAD_REQUEST
    code = "validation_error"

    def __init__(self, message: str | None = None, errors: dict | None = None):
        super().__init__(message=message or "Validation failed", code="validation_error")
        self.errors = errors or {}


class UnauthorizedError(AppError):
    http_status = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"

    def __init__(self, message: str | None = None):
        super().__init__(message=message or "Authentication required", code="unauthorized")


class ForbiddenError(AppError):
    http_status = status.HTTP_403_FORBIDDEN
    code = "forbidden"

    def __init__(self, message: str | None = None):
        super().__init__(message=message or "Permission denied", code="forbidden")


class ConflictError(AppError):
    http_status = status.HTTP_409_CONFLICT
    code = "conflict"

    def __init__(self, message: str | None = None):
        super().__init__(message=message or "Resource conflict", code="conflict")


class ExternalServiceError(AppError):
    http_status = status.HTTP_502_BAD_GATEWAY
    code = "external_service_error"

    def __init__(self, service: str = "External service", message: str | None = None):
        super().__init__(
            message=message or f"{service} is currently unavailable",
            code="external_service_error",
        )
