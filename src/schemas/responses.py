from ..schemas.models import (
    Login200,
    Login401,
    Login403,
    Logout200,
    NotFound404,
    Exception500,
    Unauthorized401,
    Forbidden403,
    Default,
)

LOGIN_RESPONSE_MODEL = {
    200: {"model": Login200},
    401: {"model": Login401},
    403: {"model": Login403},
    404: {"model": NotFound404},
    500: {"model": Exception500},
}

LOGOUT_RESPONSE_MODEL = {
    200: {"model": Logout200},
    401: {"model": Unauthorized401},
    403: {"model": Forbidden403},
    404: {"model": NotFound404},
    500: {"model": Exception500},
}

API_RESPONSE_MODEL = {
    200: {"model": Default},
    401: {"model": Unauthorized401},
    403: {"model": Forbidden403},
    404: {"model": NotFound404},
    500: {"model": Exception500},
}
