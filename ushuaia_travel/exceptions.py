import logging
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from hotels.exceptions import AppError

logger = logging.getLogger(__name__)


def api_response(success: bool, data=None, error: dict | None = None, status_code: int = 200):
    payload = {"success": success}
    if data is not None:
        payload["data"] = data
    if error is not None:
        payload["error"] = error
    return Response(payload, status=status_code)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": _map_drf_code(response.status_code),
                    "message": str(exc.detail) if hasattr(exc, "detail") else str(exc),
                },
            },
            status=response.status_code,
        )

    if isinstance(exc, AppError):
        logger.warning(
            f"AppError: {exc.code} - {exc.message}",
            extra={"error_code": exc.code, "path": context.get("request").path if context.get("request") else None},
        )
        return Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    **(exc.errors if hasattr(exc, "errors") else {}),
                },
            },
            status=exc.http_status,
        )

    logger.exception(f"Unhandled exception: {str(exc)}")
    return Response(
        {
            "success": False,
            "data": None,
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _map_drf_code(http_status_code: int) -> str:
    mapping = {
        400: "validation_error",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        406: "not_acceptable",
        409: "conflict",
        415: "unsupported_media_type",
        422: "unprocessable_entity",
        429: "too_many_requests",
        500: "internal_error",
    }
    return mapping.get(http_status_code, "error")
