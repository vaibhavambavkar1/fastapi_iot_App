from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, payload: DeviceCreate) -> Device:
        device = Device(
            device_key=payload.device_key,
            name=payload.name,
            device_type=payload.device_type,
            status=payload.status,
        )

        self._session.add(device)
        self._session.flush()

        return device

    def get_by_id(self, device_id: int) -> Device | None:
        return self._session.get(Device, device_id)

    def get_by_device_key(self, device_key: str) -> Device | None:
        statement = select(Device).where(Device.device_key == device_key)
        return self._session.scalar(statement)

    def list_devices(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Device]:
        statement = select(Device).order_by(Device.id).offset(skip).limit(limit)

        return self._session.scalars(statement).all()

    def update(
        self,
        device: Device,
        payload: DeviceUpdate,
    ) -> Device:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(device, field, value)

        self._session.flush()

        return device

    def delete(self, device: Device) -> None:
        self._session.delete(device)
        self._session.flush()
