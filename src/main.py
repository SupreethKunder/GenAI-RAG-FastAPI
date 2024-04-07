from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from .views import auth, movies
from .middleware.limiters import RateLimitMiddleware
from .schemas.requests import get_code_samples
from .core.config import settings
import functools
import io
import yaml
from contextlib import asynccontextmanager
from .controllers.misc_services import SlidingWindowRateLimiter, Rate
from .core.enums import RatePeriod
from .core.exceptions import BackendError
from .controllers.movies_services import persist_vectors_to_db
from .middleware.csrf import CSRFMiddleware

description = """
Application of RAG (GenAI)
"""
tags_metadata = [
    {
        "name": "API HTTP Responses",
        "description": "Apart from the response codes specified in each API, the API server may respond with certain 4xx and 5xx error codes which are related to common API Gateway behaviours. The application should address them accordingly.",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    persist_vectors_to_db()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000",
]

# cross origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=SlidingWindowRateLimiter(
        rate=Rate(number=60, period=RatePeriod.MINUTE)
    ),
)
app.add_middleware(CSRFMiddleware)


app.include_router(auth.router)
app.include_router(movies.router)


@app.exception_handler(RequestValidationError)
def custom_form_validation_error(request: Request, exc: RequestValidationError):
    error_list = []
    for pydantic_error in exc.errors():
        error_list.append(
            {pydantic_error["loc"][1]: pydantic_error["msg"].capitalize()}
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"errors": error_list}),
    )


@app.exception_handler(BackendError)
def custom_backend_exception(request: Request, exc: BackendError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message},
        headers=exc.headers,
    )


def custom_openapi():
    # cache the generated schema
    if app.openapi_schema:
        return app.openapi_schema

    # custom settings
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description=description,
        routes=app.routes,
        tags=tags_metadata,
        contact={
            "name": "For support contact SIRPI Team at:",
            "email": "sirpi@sirpi.io",
        },
    )

    for route in app.routes:
        if (
            ".json" not in route.path
            and ".yaml" not in route.path
            and "/docs" not in route.path
            and "/docs/oauth2-redirect" not in route.path
            and "/redoc" not in route.path
        ):
            for method in route.methods:
                if method.lower() in openapi_schema["paths"][route.path]:
                    code_samples = get_code_samples(route=route, method=method)
                    openapi_schema["paths"][route.path][method.lower()][
                        "x-codeSamples"
                    ] = code_samples

    app.openapi_schema = openapi_schema

    return app.openapi_schema


# assign the customized OpenAPI schema
app.openapi = custom_openapi


@app.get("/openapi.yaml", include_in_schema=False)
@functools.lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type="text/yaml")
