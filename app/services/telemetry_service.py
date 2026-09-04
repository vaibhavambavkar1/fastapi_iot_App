import asyncio
import json
import logging
import random
import time
from collections.abc import AsyncGenerator, AsyncIterable, Generator
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessValidationError, NotFoundError
from app.repositories.device_repository import DeviceRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry import TelemetryBatchIngestResult

logger = logging.getLogger("app.service.telemetry")


class TelemetryService:
    def __init__(self, session: Session):
        self._session = session
        self._device_repo = DeviceRepository(session)
        self._telemetry_repo = TelemetryRepository(session)

    def _ensure_device_exists(self, device_id: int) -> None:
        device = self._device_repo.get_by_id(device_id)
        if not device:
            raise NotFoundError(message=f"Device with id '{device_id}' was not found.")

    def _ensure_device_key_exists(self, device_key: str) -> None:
        device = self._device_repo.get_by_device_key(device_key)
        if not device:
            raise NotFoundError(
                message=f"Device with key '{device_key}' was not found."
            )

    # -------------------------------------------------------------------------
    # Generator 1: Telemetry CSV/JSON Export (Memory-bounded Stream)
    # -------------------------------------------------------------------------
    def export_csv(
        self,
        device_id: int,
        batch_size: int = 500,
    ) -> Generator[str, None, None]:
        """Yields CSV formatted telemetry records as a memory-efficient stream."""
        self._ensure_device_exists(device_id)

        yield "id,device_id,metric,value,recorded_at\n"

        for record in self._telemetry_repo.stream_by_device(
            device_id, batch_size=batch_size
        ):
            yield (
                f"{record.id},{record.device_id},{record.metric},"
                f"{record.value},{record.recorded_at.isoformat()}\n"
            )

    def export_ndjson(
        self,
        device_id: int,
        batch_size: int = 500,
    ) -> Generator[str, None, None]:
        """Yields newline-delimited JSON (NDJSON) telemetry records as a stream."""
        self._ensure_device_exists(device_id)

        for record in self._telemetry_repo.stream_by_device(
            device_id, batch_size=batch_size
        ):
            payload = {
                "id": record.id,
                "device_id": record.device_id,
                "metric": record.metric,
                "value": record.value,
                "recorded_at": record.recorded_at.isoformat(),
            }
            yield json.dumps(payload) + "\n"

    # -------------------------------------------------------------------------
    # Generator 2: Server-Sent Events (SSE) Live Telemetry Stream
    # -------------------------------------------------------------------------
    async def stream_live_events(
        self,
        device_key: str,
        max_events: int | None = None,
        interval_sec: float = 1.0,
    ) -> AsyncGenerator[str, None]:
        """Yields real-time Server-Sent Events (SSE) for device telemetry monitoring."""
        self._ensure_device_key_exists(device_key)

        metrics = ["temperature", "humidity", "voltage", "pressure", "vibration"]
        event_count = 0

        logger.info(
            "Starting live SSE stream for device", extra={"device_key": device_key}
        )

        try:
            while True:
                if max_events is not None and event_count >= max_events:
                    break

                metric = random.choice(metrics)
                value = round(random.uniform(15.0, 95.0), 2)
                now_str = datetime.now(UTC).isoformat()

                event_data = {
                    "device_key": device_key,
                    "metric": metric,
                    "value": value,
                    "timestamp": now_str,
                }

                # SSE protocol format: "data: <json-payload>\n\n"
                yield f"data: {json.dumps(event_data)}\n\n"
                event_count += 1

                await asyncio.sleep(interval_sec)
        except asyncio.CancelledError:
            logger.info(
                "Client disconnected from SSE stream",
                extra={"device_key": device_key},
            )
            raise

    # -------------------------------------------------------------------------
    # Generator 3: Large Data Ingestion Stream
    # -------------------------------------------------------------------------
    async def _iter_lines_from_stream(
        self, byte_stream: AsyncIterable[bytes]
    ) -> AsyncGenerator[str, None]:
        """Decodes incoming arbitrary network chunks into discrete lines without

        buffering the whole payload in memory.
        """
        buffer = ""
        async for chunk in byte_stream:
            buffer += chunk.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                stripped = line.strip("\r").strip()
                if stripped:
                    yield stripped

        final_line = buffer.strip("\r").strip()
        if final_line:
            yield final_line

    async def ingest_csv_stream(
        self,
        device_id: int,
        byte_stream: AsyncIterable[bytes],
        batch_size: int = 500,
    ) -> TelemetryBatchIngestResult:
        """Consumes a streaming byte payload, parses CSV rows line-by-line using a

        generator, and flushes to the database in bounded batches.
        """
        self._ensure_device_exists(device_id)

        start_time = time.perf_counter()
        total_ingested = 0
        batch: list[dict[str, Any]] = []
        is_header = True

        async for line in self._iter_lines_from_stream(byte_stream):
            if is_header and ("metric" in line.lower() or "value" in line.lower()):
                is_header = False
                continue
            is_header = False

            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue

            metric = parts[0]
            try:
                value = float(parts[1])
            except ValueError:
                raise BusinessValidationError(
                    message=f"Invalid numeric value in telemetry row: '{parts[1]}'"
                ) from None

            batch.append(
                {
                    "device_id": device_id,
                    "metric": metric,
                    "value": value,
                }
            )

            if len(batch) >= batch_size:
                inserted = self._telemetry_repo.bulk_insert(batch)
                total_ingested += inserted
                batch.clear()

        # Flush any remaining rows
        if batch:
            inserted = self._telemetry_repo.bulk_insert(batch)
            total_ingested += inserted
            batch.clear()

        self._session.commit()

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Batch ingestion completed",
            extra={
                "device_id": device_id,
                "ingested_count": total_ingested,
                "duration_ms": duration_ms,
            },
        )

        return TelemetryBatchIngestResult(
            device_id=device_id,
            ingested_count=total_ingested,
            duration_ms=duration_ms,
        )
