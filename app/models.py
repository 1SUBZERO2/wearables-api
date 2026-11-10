from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    patient_ref: Mapped[str] = mapped_column(String(64), index=True)
    type: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16))
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    measurement_id: Mapped[int] = mapped_column(
        ForeignKey("measurements.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )