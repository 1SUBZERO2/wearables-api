from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeasurementType(str, Enum):
    heart_rate = "heart_rate"
    steps = "steps"
    spo2 = "spo2"
    sleep_minutes = "sleep_minutes"


class MeasurementIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    patient_ref: str = Field(min_length=1, max_length=64)
    type: MeasurementType
    value: float
    unit: str = Field(min_length=1, max_length=16)
    measured_at: datetime

    @field_validator("measured_at")
    @classmethod
    def to_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class MeasurementOut(MeasurementIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class OutboxOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    measurement_id: int
    status: str
    attempts: int
    last_error: str | None
    created_at: datetime
    sent_at: datetime | None