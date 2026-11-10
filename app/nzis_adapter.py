import os
from datetime import datetime, timezone

import httpx

from app.models import Measurement

NZIS_BASE_URL = os.getenv("NZIS_BASE_URL", "http://127.0.0.1:9000")

# type -> (LOINC code, display name, category, UCUM unit code, unit text)
CODES = {
    "heart_rate": ("8867-4", "Heart rate", "vital-signs", "/min", "beats/minute"),
    "steps": (
        "55423-8",
        "Number of steps in unspecified time Pedometer",
        "activity",
        "{steps}",
        "steps",
    ),
    "spo2": (
        "59408-5",
        "Oxygen saturation in Arterial blood by Pulse oximetry",
        "vital-signs",
        "%",
        "%",
    ),
    "sleep_minutes": ("93832-4", "Sleep duration", "activity", "min", "min"),
}


def to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def build_observation(measurement: Measurement) -> dict:
    loinc, display, category, ucum, unit_text = CODES[measurement.type]
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": category,
                    }
                ]
            }
        ],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": loinc, "display": display}]
        },
        "subject": {"reference": f"Patient/{measurement.patient_ref}"},
        "device": {"reference": f"Device/{measurement.device_id}"},
        "effectiveDateTime": to_utc_iso(measurement.measured_at),
        "valueQuantity": {
            "value": measurement.value,
            "unit": unit_text,
            "system": "http://unitsofmeasure.org",
            "code": ucum,
        },
    }


def send_observation(client: httpx.Client, observation: dict) -> None:
    response = client.post(f"{NZIS_BASE_URL}/fhir/Observation", json=observation)
    response.raise_for_status()