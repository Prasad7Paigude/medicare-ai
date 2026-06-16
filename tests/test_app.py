"""Basic smoke tests for the MediCare Flask application.

Verifies that the application factory creates a working Flask instance
without requiring live external services (MongoDB, aiXplain, SMTP).
"""

import pytest


@pytest.fixture
def app():
    from src.app import create_app

    application = create_app()
    application.config.update(
        {
            "TESTING": True,
        }
    )
    yield application


def test_app_creates_successfully(app):
    assert app is not None
    assert app.name == "src.app"


def test_root_route_returns_200(app):
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_static_file_serving_returns_200(app):
    client = app.test_client()
    resp = client.get("/index.html")
    assert resp.status_code == 200
