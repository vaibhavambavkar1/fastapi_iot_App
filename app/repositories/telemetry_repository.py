from collections.abc import Generator
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.models.telemetry import TelemetryRecord


class TelemetryRepository:
    def __init__(self, session: Session):
        self._session = session

    def stream_by_device(
        self,
        device_id: int,
        batch_size: int = 500,
    ) -> Generator[TelemetryRecord, None, None]:
        """Stream telemetry records for a device using SQLAlchemy's cursor yield_per

        to ensure bounded, O(1) memory usage regardless of table size.
        """
        stmt = (
            select(TelemetryRecord)
            .where(TelemetryRecord.device_id == device_id)
            .order_by(TelemetryRecord.recorded_at.asc())
        )
        yield from self._session.scalars(stmt).yield_per(batch_size)

    def bulk_insert(self, records: list[dict[str, Any]]) -> int:
        """Insert a batch of telemetry records in a single query."""
        if not records:
            return 0
        self._session.execute(insert(TelemetryRecord), records)
        self._session.flush()
        return len(records)

    def add(
        self,
        device_id: int,
        metric: str,
        value: float,
    ) -> TelemetryRecord:
        record = TelemetryRecord(
            device_id=device_id,
            metric=metric,
            value=value,
        )
        self._session.add(record)
        self._session.flush()
        return record
