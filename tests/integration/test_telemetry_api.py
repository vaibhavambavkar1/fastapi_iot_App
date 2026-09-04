import json


def _setup_device(client, device_key="dev-int-01"):
    res = client.post(
        "/api/v1/devices",
        json={
            "device_key": device_key,
            "name": "Integration Test Device",
            "device_type": "sensor",
            "status": "active",
        },
    )
    assert res.status_code == 201
    return res.json()


def test_telemetry_csv_ingest_and_export_stream(client):
    device = _setup_device(client, "dev-telemetry-01")
    device_id = device["id"]

    # 1. Ingest telemetry using streaming CSV payload
    csv_payload = "metric,value\ntemperature,21.5\nhumidity,58.0\nvoltage,3.31\n"
    ingest_res = client.post(
        f"/api/v1/devices/{device_id}/telemetry/ingest",
        content=csv_payload.encode("utf-8"),
        headers={"Content-Type": "text/csv"},
    )
    assert ingest_res.status_code == 201
    result_data = ingest_res.json()
    assert result_data["ingested_count"] == 3
    assert result_data["device_id"] == device_id

    # 2. Export as CSV via generator stream
    export_csv_res = client.get(
        f"/api/v1/devices/{device_id}/telemetry/export?format=csv"
    )
    assert export_csv_res.status_code == 200
    assert "text/csv" in export_csv_res.headers["content-type"]
    csv_text = export_csv_res.text
    assert "id,device_id,metric,value,recorded_at" in csv_text
    assert "temperature,21.5" in csv_text
    assert "humidity,58.0" in csv_text
    assert "voltage,3.31" in csv_text

    # 3. Export as NDJSON via generator stream
    export_json_res = client.get(
        f"/api/v1/devices/{device_id}/telemetry/export?format=json"
    )
    assert export_json_res.status_code == 200
    assert "application/x-ndjson" in export_json_res.headers["content-type"]
    lines = [
        json.loads(line) for line in export_json_res.text.strip().split("\n") if line
    ]
    assert len(lines) == 3
    assert lines[0]["metric"] == "temperature"
    assert lines[0]["value"] == 21.5


def test_telemetry_live_sse_stream(client):
    device = _setup_device(client, "dev-sse-01")
    device_key = device["device_key"]

    # Request SSE with max_events=2
    response = client.get(f"/api/v1/devices/{device_key}/telemetry/live?max_events=2")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    events = [
        ev for ev in response.text.strip().split("\n\n") if ev.startswith("data: ")
    ]
    assert len(events) == 2
    for event_raw in events:
        event_json = json.loads(event_raw[len("data: ") :])
        assert event_json["device_key"] == device_key
        assert "metric" in event_json
        assert "value" in event_json
