def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_device_success(client):
    payload = {
        "device_key": "sensor-001",
        "name": "Temperature Sensor A",
        "device_type": "sensor",
        "status": "active",
    }

    response = client.post("/api/v1/devices", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["device_key"] == payload["device_key"]
    assert body["name"] == payload["name"]
    assert body["status"] == "active"
    assert "id" in body
    assert "created_at" in body


def test_create_device_conflict(client):
    payload = {
        "device_key": "sensor-002",
        "name": "Temperature Sensor B",
        "device_type": "sensor",
        "status": "active",
    }

    first_response = client.post("/api/v1/devices", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/api/v1/devices", json=payload)

    assert second_response.status_code == 409

    body = second_response.json()
    assert body["error"]["code"] == "conflict"


def test_get_device_success(client):
    payload = {
        "device_key": "sensor-003",
        "name": "Pressure Sensor",
        "device_type": "sensor",
        "status": "active",
    }

    create_response = client.post("/api/v1/devices", json=payload)
    device_id = create_response.json()["id"]

    response = client.get(f"/api/v1/devices/{device_id}")

    assert response.status_code == 200
    assert response.json()["id"] == device_id


def test_get_device_not_found(client):
    response = client.get("/api/v1/devices/9999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_update_device_success(client):
    payload = {
        "device_key": "sensor-004",
        "name": "Humidity Sensor",
        "device_type": "sensor",
        "status": "active",
    }

    create_response = client.post("/api/v1/devices", json=payload)
    device_id = create_response.json()["id"]

    update_payload = {
        "status": "maintenance",
    }

    response = client.patch(
        f"/api/v1/devices/{device_id}",
        json=update_payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "maintenance"


def test_delete_device_success(client):
    payload = {
        "device_key": "sensor-005",
        "name": "Flow Sensor",
        "device_type": "sensor",
        "status": "active",
    }

    create_response = client.post("/api/v1/devices", json=payload)
    device_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/devices/{device_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404
