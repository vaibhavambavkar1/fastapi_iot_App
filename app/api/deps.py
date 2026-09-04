from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.device_service import DeviceService
from app.services.telemetry_service import TelemetryService


def get_device_service(
    db: Session = Depends(get_db),
) -> DeviceService:
    return DeviceService(db)


def get_telemetry_service(
    db: Session = Depends(get_db),
) -> TelemetryService:
    return TelemetryService(db)
