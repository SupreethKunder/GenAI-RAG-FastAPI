from fastapi.testclient import TestClient
from src.main import app
from src.middleware.islogin import oauth2_scheme, mock_oauth
from src.core.config import settings
import pytest
import uuid

STATUS_CODES = [200, 400, 401, 403, 404, 422, 429, 500, 502, 503, 504]
client = TestClient(app)
app.dependency_overrides[oauth2_scheme] = mock_oauth


def request_headers(status_code):
    return {"X-Mock-Request": f"yes_{status_code}"}


def test_login():
    request_data = {"username": settings.TEST_LOGIN, "password": settings.TEST_PASSWORD}
    request_cookies = {"csrftoken": uuid.uuid4().hex}
    response = client.post(
        "/login", data=request_data, cookies=request_cookies, headers=request_cookies
    )
    assert response.status_code == 200


@pytest.mark.parametrize("status_code", STATUS_CODES)
def test_logout(status_code):
    response = client.get(
        "/logout",
        headers=request_headers(status_code),
    )
    assert response.status_code == status_code
