from backend.app import create_app
from unittest.mock import patch


def test_health_and_status_without_hardware():
    app, _ = create_app("mac")
    client = app.test_client()

    assert client.get("/health").get_json() == {"status": "ok", "profile": "mac"}
    status = client.get("/api/v1/status").get_json()
    assert status["profile"] == "mac"
    assert status["connection"]["status"] == "disconnected"
    assert status["trackPower"] == "off"


def test_built_frontend_is_served():
    app, _ = create_app("mac")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b'<div id="root"></div>' in response.data
    assert b'width=device-width, initial-scale=1, viewport-fit=cover' in response.data

    javascript_path = response.data.decode().split('src="')[1].split('"')[0]
    javascript = client.get(javascript_path)
    assert javascript.status_code == 200
    assert javascript.mimetype == "text/javascript"


def test_serial_os_permission_error_returns_conflict():
    app, _ = create_app("mac")
    controller = app.extensions["csb1_controller"]
    with patch.object(controller, "connect", side_effect=RuntimeError("permission denied")):
        response = app.test_client().post("/api/v1/serial/connect", json={})
    assert response.status_code == 409
    assert response.get_json() == {"error": "permission denied"}


def test_locomotive_roster_endpoint():
    app, _ = create_app("mac")
    response = app.test_client().get("/api/v1/locomotives")
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == len(body["locomotives"])
    assert all(item["status"] == "active" for item in body["locomotives"])
