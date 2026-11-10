from fastapi import Depends, FastAPI, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db
from app.security import require_api_key

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wearables API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/measurements",
    response_model=schemas.MeasurementOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_measurement(payload: schemas.MeasurementIn, db: Session = Depends(get_db)):
    measurement = models.Measurement(
        device_id=payload.device_id,
        patient_ref=payload.patient_ref,
        type=payload.type.value,
        value=payload.value,
        unit=payload.unit,
        measured_at=payload.measured_at,
    )
    db.add(measurement)
    db.flush()
    db.add(models.OutboxMessage(measurement_id=measurement.id))
    db.commit()
    db.refresh(measurement)
    return measurement


@app.get(
    "/measurements",
    response_model=list[schemas.MeasurementOut],
    dependencies=[Depends(require_api_key)],
)
def list_measurements(
    patient_ref: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = select(models.Measurement).order_by(models.Measurement.id.desc()).limit(limit)
    if patient_ref:
        query = query.where(models.Measurement.patient_ref == patient_ref)
    return db.scalars(query).all()


@app.get(
    "/outbox",
    response_model=list[schemas.OutboxOut],
    dependencies=[Depends(require_api_key)],
)
def list_outbox(
    outbox_status: str | None = Query(default=None, alias="status"),
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = select(models.OutboxMessage).order_by(models.OutboxMessage.id.desc()).limit(limit)
    if outbox_status:
        query = query.where(models.OutboxMessage.status == outbox_status)
    return db.scalars(query).all()