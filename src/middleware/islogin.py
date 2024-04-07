from typing import Optional
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)
from starlette.requests import Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from ..database.connect import redis_client
from ..core.config import settings
import pickle


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        cookie_authorization: str = request.cookies.get("Authorization")
        auth = get_authorization_scheme_param(cookie_authorization)
        if len(auth) > 2:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Authorization cookies must be a Bearer token",
                )
            else:
                return None
        cookie_scheme, cookie_param = auth
        # print(cookie_scheme)
        if cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

            try:
                data = redis_client.get(param)
                cache = pickle.loads(data)
            except Exception:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Token expired"
                )

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Authorization cookies must start with Bearer",
                )
            else:
                return None
        # Idempotency
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            requestID = request.headers.get("X-Request-ID", None)
            p_requestID = cache.get("requestID", None)
            if not requestID:
                if self.auto_error:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="Request ID must be provided for Idempotency",
                    )
            if requestID == p_requestID:
                if self.auto_error:
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="Duplicate Request has been made. Please renew the request token for Idempotency",
                    )
            if not p_requestID or requestID != p_requestID:
                cache["requestID"] = requestID
                redis_client.set(param, pickle.dumps([cache]))
        return [param, cache]


class MockOauth(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        mock: str = request.headers.get("X-Mock-Request")
        ismock, flow = mock.split("_")
        if ismock == "yes":
            if flow == "400":
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
            elif flow == "401":
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            elif flow == "403":
                raise HTTPException(status_code=HTTP_403_FORBIDDEN)
            elif flow == "404":
                raise HTTPException(status_code=HTTP_404_NOT_FOUND)
            elif flow == "405":
                raise HTTPException(status_code=HTTP_405_METHOD_NOT_ALLOWED)
            elif flow == "422":
                raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)
            elif flow == "429":
                raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS)
            elif flow == "500":
                raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
            elif flow == "502":
                raise HTTPException(status_code=HTTP_502_BAD_GATEWAY)
            elif flow == "503":
                raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE)
            elif flow == "504":
                raise HTTPException(status_code=HTTP_504_GATEWAY_TIMEOUT)
        cache = {"email": settings.TEST_LOGIN, "requestID": None}
        return ["token", cache]


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/")
mock_oauth = MockOauth(tokenUrl="/")
