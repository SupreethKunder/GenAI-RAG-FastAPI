from fastapi import Query, Form
from pydantic import EmailStr, SecretStr, BaseModel
from enum import Enum


class Exception500(BaseModel):
    message: str


class NotFound404(BaseModel):
    message: str = "Not Found"


class Forbidden(str, Enum):
    a = "Authorization cookies must start with Bearer"
    b = "Authorization cookies must be a Bearer token"
    c = "Forbidden Access"


class Unauthorized(str, Enum):
    a = "Token expired"
    b = "Unauthorized"


class Forbidden403(BaseModel):
    detail: Forbidden = "Forbidden Access"


class Unauthorized401(BaseModel):
    message: Unauthorized = "Unauthorized"


class Login200(BaseModel):
    token: str


class Default(BaseModel):
    message: str


class Home200(BaseModel):
    message: str = "This is initial route of Windvista Project MS"


class Login403(BaseModel):
    message: str = "Wrong email or password"


class Login401(BaseModel):
    message: str = "Invalid Client ID or Secret"


class Logout200(BaseModel):
    message: str = "Logged out successfully"


class Login:
    def __init__(
        self,
        username: EmailStr = Form(..., description="Registered Email ID"),
        password: SecretStr = Form(..., description="Password"),
    ):
        self.username = username
        self.password = password


class GetMovies:
    def __init__(
        self,
        query: str = Query(..., description="Query for prompts"),
    ):
        self.query = query
