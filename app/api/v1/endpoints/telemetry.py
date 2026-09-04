from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_telemetry_service
from app.schemas.telemetry import TelemetryBatchIngestResult
from app.services.telemetry_service import TelemetryService

router = APIRouter()


@router.get(
    "/devices/{device_id}/telemetry/export",
    summary="Export telemetry records as a memory-bounded stream",
    responses={
        200: {
            "description": "Streamed telemetry data (CSV or NDJSON)",
            "content": {
                "text/csv": {},
                "application/x-ndjson": {},
            },
        }
    },
)
def export_telemetry(
    device_id: int,
    format: str = Query(
        default="csv",
        pattern="^(csv|json)$",
        description="Format: 'csv' for text/csv or 'json' for newline-delimited JSON",
    ),
    service: TelemetryService = Depends(get_telemetry_service),
) -> StreamingResponse:
    if format == "json":
        filename = f"device_{device_id}_telemetry.ndjson"
        return StreamingResponse(
            service.export_ndjson(device_id),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    filename = f"device_{device_id}_telemetry.csv"
    return StreamingResponse(
        service.export_csv(device_id),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/devices/{device_key}/telemetry/live",
    summary="Subscribe to real-time live device telemetry via Server-Sent Events (SSE)",
    responses={
        200: {
            "description": "Server-Sent Events event stream",
            "content": {"text/event-stream": {}},
        }
    },
)
def stream_live_telemetry(
    device_key: str,
    max_events: int | None = Query(
        default=None,
        ge=1,
        le=1000,
        description="Optional limit on number of events to stream (useful for testing)",
    ),
    service: TelemetryService = Depends(get_telemetry_service),
) -> StreamingResponse:
    return StreamingResponse(
        service.stream_live_events(device_key, max_events=max_events),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/devices/{device_id}/telemetry/ingest",
    response_model=TelemetryBatchIngestResult,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest large telemetry CSV streams line-by-line using generators",
)
async def ingest_telemetry_stream(
    device_id: int,
    request: Request,
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryBatchIngestResult:
    return await service.ingest_csv_stream(
        device_id=device_id,
        byte_stream=request.stream(),
    )
