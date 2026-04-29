import logging
import time
from uuid import uuid4


AUDIT_LOGGER = logging.getLogger("campaign.audit")


class RequestAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.request_id = request_id
        start = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start) * 1000
        user = getattr(request, "user", None)
        user_id = user.pk if getattr(user, "is_authenticated", False) else None
        AUDIT_LOGGER.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f user_id=%s",
            request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            user_id,
        )
        response["X-Request-ID"] = request_id
        return response
