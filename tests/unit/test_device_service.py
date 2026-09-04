import pytest

from app.core.exceptions import ConflictError
from app.schemas.device import DeviceCreate
from app.services.device_service import DeviceService


def test_device_service_creates_device(db_session):
    service = DeviceService(db_session)

    payload = DeviceCreate(
        device_key="sensor-100",
        name="Test Sensor",
        device_type="sensor",
        status="active",
    )

    device = service.create_device(payload)

    assert device.id is not None
    assert device.device_key == payload.device_key


def test_device_service_prevents_duplicate_device_key(db_session):
    service = DeviceService(db_session)

    payload = DeviceCreate(
        device_key="sensor-101",
        name="Test Sensor",
        device_type="sensor",
        status="active",
    )

    service.create_device(payload)

    with pytest.raises(ConflictError):
        service.create_device(payload)
