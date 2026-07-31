import os
import jwt
from typing import Any
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 7


def create_jwt(payload: dict[str, Any]) -> str:
    to_encode = payload.copy()

    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
        days=JWT_EXPIRY_DAYS
    )

    token = jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return token