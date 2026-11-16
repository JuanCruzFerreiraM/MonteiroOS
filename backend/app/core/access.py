import secrets

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

ACCESS_HEADER = "x-monteiro-access"
PUBLIC_ROUTES = {("GET", "/health")}


def secrets_match(provided: str, expected: str) -> bool:
    return secrets.compare_digest(
        provided.encode("utf-8"),
        expected.encode("utf-8"),
    )


class DeploymentAccessMiddleware(BaseHTTPMiddleware):
    """Gate every route except public health checks when a deployment secret is set.

    An empty secret leaves the API open. Local Compose relies on loopback port
    bindings in that mode. The secret does not identify a person.
    """

    def __init__(self, app: object, secret: str) -> None:
        super().__init__(app)
        self._secret = secret

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if self._secret == "":
            return await call_next(request)
        if (request.method, request.url.path) in PUBLIC_ROUTES:
            return await call_next(request)
        provided = request.headers.get(ACCESS_HEADER, "")
        if not secrets_match(provided, self._secret):
            return JSONResponse(status_code=401, content={"detail": "access denied"})
        return await call_next(request)
