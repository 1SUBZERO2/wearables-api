import time

from app import models  # noqa: F401  (registers the tables)
from app.database import Base, SessionLocal, engine
from app.outbox_worker import process_pending


def main(interval: float = 5.0) -> None:
    Base.metadata.create_all(bind=engine)
    print(f"Outbox worker started, checking every {interval} seconds")
    while True:
        db = SessionLocal()
        try:
            result = process_pending(db)
            if result["processed"]:
                print(result)
        except Exception as error:  # keep the worker alive
            print(f"Worker error: {error}")
        finally:
            db.close()
        time.sleep(interval)


if __name__ == "__main__":
    main()