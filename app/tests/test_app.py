import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"8Byte.ai DevOps CI/CD Demo" in response.data


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_version():
    client = app.test_client()

    response = client.get("/version")

    assert response.status_code == 200
    assert response.get_json()["version"] == "1.0"