from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ..core.exceptions import BackendError


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        try:
            rate_limit_headers = await self.rate_limiter(
                request=request, response=Response()
            )
            response = await call_next(request)
            response.headers.update(rate_limit_headers)
            return response
        except BackendError as exc:
            return JSONResponse(
                status_code=exc.code,
                content={"message": exc.message},
                headers=exc.headers,
            )
