import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("request")


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())[:8]

    def process_response(self, request, response):
        duration_ms = round((time.time() - request.start_time) * 1000, 2)
        logger.info(
            f"{request.method} {request.path} -> {response.status_code} ({duration_ms}ms)",
            extra={
                "request_id": getattr(request, "request_id", "-"),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
