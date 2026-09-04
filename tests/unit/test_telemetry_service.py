import json
from collections.abc import AsyncGenerator

import pytest

from app.core.exceptions import BusinessValidationError, NotFoundError
from app.models.device import Device
from app.models.telemetry import TelemetryRecord
from app.services.telemetry_service import TelemetryService


def _create_test_device(session, device_key="sensor-gen-1"):
    device = Device(
        device_key=device_key,
        name="Generator Test Sensor",
        device_type="sensor",
        status="active",
    )
    session.add(device)
    session.commit()
    return device


def test_export_csv_generator(db_session):
    device = _create_test_device(db_session, "sensor-gen-csv")
    t1 = TelemetryRecord(device_id=device.id, metric="temperature", value=22.5)
    t2 = TelemetryRecord(device_id=device.id, metric="humidity", value=55.0)
    db_session.add_all([t1, t2])
    db_session.commit()

    service = TelemetryService(db_session)
    csv_gen = service.export_csv(device.id)

    lines = list(csv_gen)
    assert len(lines) == 3
    assert lines[0] == "id,device_id,metric,value,recorded_at\n"
    assert "temperature" in lines[1]
    assert "22.5" in lines[1]
    assert "humidity" in lines[2]


def test_export_ndjson_generator(db_session):
    device = _create_test_device(db_session, "sensor-gen-json")
    t1 = TelemetryRecord(device_id=device.id, metric="voltage", value=3.3)
    db_session.add(t1)
    db_session.commit()

    service = TelemetryService(db_session)
    json_gen = service.export_ndjson(device.id)

    lines = list(json_gen)
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["metric"] == "voltage"
    assert data["value"] == 3.3
    assert data["device_id"] == device.id


def test_export_non_existent_device_raises_not_found(db_session):
    service = TelemetryService(db_session)
    with pytest.raises(NotFoundError):
        list(service.export_csv(99999))


@pytest.mark.anyio
async def test_stream_live_events_sse(db_session):
    device = _create_test_device(db_session, "sensor-gen-sse")
    service = TelemetryService(db_session)

    events = []
    async for event_str in service.stream_live_events(
        device.device_key, max_events=3, interval_sec=0.01
    ):
        events.append(event_str)

    assert len(events) == 3
    for ev in events:
        assert ev.startswith("data: ")
        assert ev.endswith("\n\n")
        payload = json.loads(ev[len("data: ") : -2])
        assert payload["device_key"] == "sensor-gen-sse"
        assert "metric" in payload
        assert "value" in payload
        assert "timestamp" in payload


@pytest.mark.anyio
async def test_ingest_csv_stream(db_session):
    device = _create_test_device(db_session, "sensor-gen-ingest")
    service = TelemetryService(db_session)

    async def mock_byte_stream() -> AsyncGenerator[bytes, None]:
        chunks = [
            b"metric,value\ntemperature",
            b",25.5\nhumidity,62.",
            b"4\npressure,1013.2\n",
        ]
        for c in chunks:
            yield c

    result = await service.ingest_csv_stream(
        device.id, mock_byte_stream(), batch_size=2
    )

    assert result.ingested_count == 3
    assert result.device_id == device.id

    # Verify rows persisted in DB
    records = db_session.query(TelemetryRecord).filter_by(device_id=device.id).all()
    assert len(records) == 3
    metrics = {r.metric: r.value for r in records}
    assert metrics["temperature"] == 25.5
    assert metrics["humidity"] == 62.4
    assert metrics["pressure"] == 1013.2


@pytest.mark.anyio
async def test_ingest_csv_stream_invalid_numeric(db_session):
    device = _create_test_device(db_session, "sensor-gen-err")
    service = TelemetryService(db_session)

    async def invalid_stream() -> AsyncGenerator[bytes, None]:
        yield b"metric,value\ntemperature,NOT_A_FLOAT\n"

    with pytest.raises(BusinessValidationError):
        await service.ingest_csv_stream(device.id, invalid_stream())
