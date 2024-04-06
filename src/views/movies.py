from fastapi import APIRouter, Depends
from ..schemas.responses import API_RESPONSE_MODEL
from fastapi.responses import JSONResponse
from ..middleware.logging import logger
from ..controllers.movies_services import perform_vector_search
from typing import List, Union, Dict
from ..middleware.islogin import oauth2_scheme
from ..schemas.models import GetMovies

router = APIRouter()


@router.get(
    "/movies",
    responses=API_RESPONSE_MODEL,
    tags=["Movies"],
    operation_id="get_movies",
)
def get_movies(
    payload: GetMovies = Depends(),
    token: List[Union[str, Dict[str, str]]] = Depends(oauth2_scheme),
) -> JSONResponse:
    logger.info("%s - %s", token[1]["email"], "GET Movies API is being called")
    return perform_vector_search(query=payload.query)
