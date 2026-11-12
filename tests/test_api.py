HEADERS = {"X-API-Key": "dev-key-123"}

VALID = {
    "device_id": "band-001",
    "patient_ref": "patient-001",
    "type": "heart_rate",
    "value": 72,
    "unit": "bpm",
    "measured_at": "2026-11-10T10:30:00Z",
}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_without_api_key_is_rejected(client):
    response = client.post("/measurements", json=VALID)
    assert response.status_code == 401


def test_post_with_wrong_api_key_is_rejected(client):
    response = client.post("/measurements", json=VALID, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_post_valid_measurement_creates_record(client):
    response = client.post("/measurements", json=VALID, headers=HEADERS)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["type"] == "heart_rate"
    assert body["value"] == 72


def test_invalid_type_is_rejected(client):
    payload = {**VALID, "type": "abc"}
    response = client.post("/measurements", json=payload, headers=HEADERS)
    assert response.status_code == 422


def test_new_measurement_creates_pending_outbox_message(client):
    client.post("/measurements", json=VALID, headers=HEADERS)
    response = client.get("/outbox", headers=HEADERS)
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["status"] == "pending"
    assert messages[0]["attempts"] == 0