from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.config import settings


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def get_password_hash(password: str) -> str:
    return generate_password_hash(password)
