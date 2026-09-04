import logging
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Device
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceUpdate

logger = logging.getLogger("app.service.device")


class DeviceService:
    def __init__(self, session: Session):
        self._session = session
        self._repository = DeviceRepository(session)

    def create_device(self, payload: DeviceCreate) -> Device:
        try:
            existing_device = self._repository.get_by_device_key(payload.device_key)

            if existing_device:
                raise ConflictError(
                    message=f"Device key '{payload.device_key}' already exists."
                )

            device = self._repository.add(payload)
            self._session.commit()

            logger.info(
                "Device created successfully",
                extra={
                    "device_id": device.id,
                    "device_key": device.device_key,
                },
            )

            return device

        except ConflictError:
            self._session.rollback()
            raise

        except Exception:
            self._session.rollback()
            logger.exception("Failed to create device")
            raise

    def get_device(self, device_id: int) -> Device:
        device = self._repository.get_by_id(device_id)

        if not device:
            raise NotFoundError(message=f"Device with id '{device_id}' was not found.")

        return device

    def list_devices(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Device]:
        return self._repository.list_devices(skip=skip, limit=limit)

    def update_device(
        self,
        device_id: int,
        payload: DeviceUpdate,
    ) -> Device:
        try:
            device = self.get_device(device_id)

            updated_device = self._repository.update(
                device=device,
                payload=payload,
            )

            self._session.commit()

            logger.info(
                "Device updated successfully",
                extra={"device_id": device_id},
            )

            return updated_device

        except NotFoundError:
            self._session.rollback()
            raise

        except Exception:
            self._session.rollback()
            logger.exception("Failed to update device")
            raise

    def delete_device(self, device_id: int) -> None:
        try:
            device = self.get_device(device_id)

            self._repository.delete(device)
            self._session.commit()

            logger.info(
                "Device deleted successfully",
                extra={"device_id": device_id},
            )

        except NotFoundError:
            self._session.rollback()
            raise

        except Exception:
            self._session.rollback()
            logger.exception("Failed to delete device")
            raise
