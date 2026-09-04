from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    metric: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    device: Mapped["Device"] = relationship(
        back_populates="telemetry_records",
    )
