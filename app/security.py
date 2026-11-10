import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_valid_keys() -> set[str]:
    raw = os.getenv("API_KEYS", "dev-key-123")
    return {key.strip() for key in raw.split(",") if key.strip()}


def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    if api_key is not None:
        for valid_key in get_valid_keys():
            if secrets.compare_digest(api_key.encode(), valid_key.encode()):
                return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )