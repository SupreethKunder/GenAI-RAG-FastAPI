from fastapi.testclient import TestClient
from src.main import app
from src.middleware.islogin import oauth2_scheme, mock_oauth
import pytest

STATUS_CODES = [200, 400, 401, 403, 404, 422, 429, 500, 502, 503, 504]
client = TestClient(app)
app.dependency_overrides[oauth2_scheme] = mock_oauth


def request_headers(status_code):
    return {"X-Mock-Request": f"yes_{status_code}"}


@pytest.mark.parametrize("status_code", STATUS_CODES)
@pytest.mark.parametrize(
    "query",
    [
        "imaginary characters from outer space at war",
        "characters from Multiverse",
        "reincarnated characters",
    ],
)
def test_search_movies(status_code, query):
    response = client.get(
        f"/movies?query={query}",
        headers=request_headers(status_code),
    )
    assert response.status_code == status_code
