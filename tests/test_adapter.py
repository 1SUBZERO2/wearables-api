from datetime import datetime, timedelta, timezone

from app.models import Measurement
from app.nzis_adapter import build_observation, to_utc_iso


def test_naive_time_is_treated_as_utc():
    assert to_utc_iso(datetime(2026, 11, 10, 10, 30)) == "2026-11-10T10:30:00Z"


def test_time_with_offset_is_converted_to_utc():
    value = datetime(2026, 11, 10, 10, 30, tzinfo=timezone(timedelta(hours=2)))
    assert to_utc_iso(value) == "2026-11-10T08:30:00Z"


def test_build_observation_maps_fields():
    measurement = Measurement(
        device_id="band-001",
        patient_ref="patient-001",
        type="heart_rate",
        value=72.0,
        unit="bpm",
        measured_at=datetime(2026, 11, 10, 10, 30, tzinfo=timezone.utc),
    )
    observation = build_observation(measurement)
    assert observation["resourceType"] == "Observation"
    assert observation["code"]["coding"][0]["code"] == "8867-4"
    assert observation["subject"]["reference"] == "Patient/patient-001"
    assert observation["device"]["reference"] == "Device/band-001"
    assert observation["valueQuantity"]["value"] == 72.0
    assert observation["effectiveDateTime"].endswith("Z")