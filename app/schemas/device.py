from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    device_key: str = Field(
        min_length=3,
        max_length=120,
        examples=["sensor-001"],
    )

    name: str = Field(
        min_length=3,
        max_length=200,
        examples=["Temperature Sensor - Plant A"],
    )

    device_type: str = Field(
        default="sensor",
        max_length=80,
        examples=["sensor", "gateway", "actuator"],
    )

    status: str = Field(
        default="active",
        pattern="^(active|inactive|maintenance)$",
    )


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    device_type: str | None = Field(
        default=None,
        max_length=80,
    )

    status: str | None = Field(
        default=None,
        pattern="^(active|inactive|maintenance)$",
    )


class DeviceRead(DeviceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
