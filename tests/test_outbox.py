import httpx

from app.outbox_worker import MAX_ATTEMPTS

HEADERS = {"X-API-Key": "dev-key-123"}

VALID = {
    "device_id": "band-001",
    "patient_ref": "patient-001",
    "type": "heart_rate",
    "value": 72,
    "unit": "bpm",
    "measured_at": "2026-11-10T10:30:00Z",
}


def _failing(client, observation):
    raise httpx.ConnectError("NZIS unavailable")


def _succeeding(client, observation):
    return None


def test_successful_delivery_marks_message_sent(client, monkeypatch):
    monkeypatch.setattr("app.outbox_worker.send_observation", _succeeding)
    client.post("/measurements", json=VALID, headers=HEADERS)

    result = client.post("/outbox/process", headers=HEADERS).json()
    assert result == {"processed": 1, "sent": 1, "errors": 0}

    sent = client.get("/outbox", params={"status": "sent"}, headers=HEADERS).json()
    assert len(sent) == 1
    assert sent[0]["sent_at"] is not None


def test_failed_delivery_stays_pending_and_succeeds_on_retry(client, monkeypatch):
    client.post("/measurements", json=VALID, headers=HEADERS)

    monkeypatch.setattr("app.outbox_worker.send_observation", _failing)
    result = client.post("/outbox/process", headers=HEADERS).json()
    assert result == {"processed": 1, "sent": 0, "errors": 1}

    pending = client.get("/outbox", params={"status": "pending"}, headers=HEADERS).json()
    assert len(pending) == 1
    assert pending[0]["attempts"] == 1
    assert "NZIS unavailable" in pending[0]["last_error"]

    monkeypatch.setattr("app.outbox_worker.send_observation", _succeeding)
    result = client.post("/outbox/process", headers=HEADERS).json()
    assert result == {"processed": 1, "sent": 1, "errors": 0}


def test_message_becomes_failed_after_max_attempts(client, monkeypatch):
    monkeypatch.setattr("app.outbox_worker.send_observation", _failing)
    client.post("/measurements", json=VALID, headers=HEADERS)

    for _ in range(MAX_ATTEMPTS):
        client.post("/outbox/process", headers=HEADERS)

    failed = client.get("/outbox", params={"status": "failed"}, headers=HEADERS).json()
    assert len(failed) == 1
    assert failed[0]["attempts"] == MAX_ATTEMPTS

    result = client.post("/outbox/process", headers=HEADERS).json()
    assert result["processed"] == 0