from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


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


class MeasurementOut(MeasurementIn):
    model_config = ConfigDict(from_attributes=True)
    id: int