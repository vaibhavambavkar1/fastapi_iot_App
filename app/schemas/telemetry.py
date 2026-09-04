from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryRecordRead(BaseModel):
    id: int
    device_id: int
    metric: str
    value: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TelemetryBatchIngestResult(BaseModel):
    device_id: int
    ingested_count: int
    duration_ms: float
    status: str = "completed"


class LiveTelemetryEvent(BaseModel):
    device_key: str
    metric: str
    value: float
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp of the event")
