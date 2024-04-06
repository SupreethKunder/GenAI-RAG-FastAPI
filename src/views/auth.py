from fastapi import APIRouter, Depends
from ..controllers.authentication_services import (
    login_api,
    logout_api,
)
from ..middleware.logging import logger
from ..middleware.islogin import oauth2_scheme
from ..schemas.models import Login
from fastapi.responses import JSONResponse
from typing import List
from ..schemas.responses import LOGIN_RESPONSE_MODEL, LOGOUT_RESPONSE_MODEL

router = APIRouter()


@router.post("/login", responses=LOGIN_RESPONSE_MODEL, tags=["Authentication"])
def login(creds: Login = Depends()) -> JSONResponse:
    """
    ```
    Auth0 is an third party service by Okta, which we use for
    authentication, authorization and security.
    ```
    """
    logger.info("%s - %s", creds.username, "Login API is being called")
    return login_api(creds.username, creds.password.get_secret_value())


@router.get("/logout", responses=LOGOUT_RESPONSE_MODEL, tags=["Authentication"])
def logout(token: List = Depends(oauth2_scheme)) -> JSONResponse:
    """
    ```
    This API will revoke the access of an authenticated user
    ```
    """
    logger.info("%s - %s", token[1]["email"], "Logout API is being called")
    return logout_api(token)
