from backend.app import create_app
from unittest.mock import patch

from backend.serial.parser import ProtocolEvent


def test_health_and_status_without_hardware():
    app, _ = create_app("mac")
    client = app.test_client()

    health = client.get("/health").get_json()
    assert health["status"] == "ok"
    assert health["profile"] == "mac"
    assert isinstance(health["pid"], int)
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
    assert client.get("/shared/union-pacific-logo.png").status_code == 200


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


def test_service_track_cv_read_and_write():
    app, _ = create_app("mac")
    controller = app.extensions["csb1_controller"]
    client = app.test_client()

    responses = [
        ProtocolEvent("cv", {"cv": 29, "value": 38, "callback": 1, "callbackSub": 0}, "<r 1|0|29 38>"),
        ProtocolEvent("cv", {"cv": 29, "value": 40}, "<r 29 40>"),
    ]
    with patch.object(controller, "request", side_effect=responses) as request_command:
        read = client.post("/api/v1/programming/cv/read", json={"cv": 29})
        written = client.put("/api/v1/programming/cv", json={"cv": 29, "value": 40})

    assert read.status_code == 200
    assert read.get_json() == {"cv": 29, "value": 38, "confirmed": True, "mode": "service"}
    assert written.status_code == 200
    assert written.get_json() == {"cv": 29, "value": 40, "confirmed": True, "mode": "service"}
    assert request_command.call_count == 2


def test_service_track_cv_validation():
    app, _ = create_app("mac")
    client = app.test_client()

    assert client.post("/api/v1/programming/cv/read", json={"cv": 0}).status_code == 400
    assert client.put("/api/v1/programming/cv", json={"cv": 1, "value": 256}).status_code == 400
