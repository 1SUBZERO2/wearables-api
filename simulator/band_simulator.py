import argparse
import random
import time
from datetime import datetime, timezone

import httpx


def build_measurements(device_id: str, patient_ref: str) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    base = {"device_id": device_id, "patient_ref": patient_ref, "measured_at": now}
    return [
        {**base, "type": "heart_rate", "value": random.randint(58, 110), "unit": "bpm"},
        {**base, "type": "steps", "value": random.randint(0, 120), "unit": "count"},
        {**base, "type": "spo2", "value": round(random.uniform(94, 100), 1), "unit": "%"},
    ]


def main():
    parser = argparse.ArgumentParser(description="Wearable band simulator")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-key", default="dev-key-123")
    parser.add_argument("--device-id", default="band-001")
    parser.add_argument("--patient-ref", default="patient-001")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    headers = {"X-API-Key": args.api_key}
    with httpx.Client(base_url=args.url, headers=headers, timeout=10) as client:
        for i in range(args.count):
            for measurement in build_measurements(args.device_id, args.patient_ref):
                try:
                    response = client.post("/measurements", json=measurement)
                    print(
                        f"[{i + 1}/{args.count}] "
                        f"{measurement['type']}={measurement['value']} -> {response.status_code}"
                    )
                except httpx.HTTPError as error:
                    print(f"Connection error: {error}")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()