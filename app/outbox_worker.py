import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.models import utcnow
from app.nzis_adapter import build_observation, send_observation

MAX_ATTEMPTS = 5


def process_pending(db: Session, batch_size: int = 50) -> dict:
    messages = db.scalars(
        select(models.OutboxMessage)
        .where(models.OutboxMessage.status == "pending")
        .order_by(models.OutboxMessage.id)
        .limit(batch_size)
    ).all()

    sent = 0
    errors = 0
    with httpx.Client(timeout=5) as client:
        for message in messages:
            measurement = db.get(models.Measurement, message.measurement_id)
            message.attempts += 1
            try:
                send_observation(client, build_observation(measurement))
            except httpx.HTTPError as error:
                message.last_error = str(error)[:500]
                if message.attempts >= MAX_ATTEMPTS:
                    message.status = "failed"
                errors += 1
            else:
                message.status = "sent"
                message.sent_at = utcnow()
                message.last_error = None
                sent += 1
            db.commit()

    return {"processed": len(messages), "sent": sent, "errors": errors}