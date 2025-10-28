import datetime as dt
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import get_settings

security = HTTPBearer()
settings = get_settings()


def create_access_token(group_id: uuid.UUID, expires_delta: dt.timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = dt.timedelta(hours=12)
    expire = dt.datetime.utcnow() + expires_delta
    payload = {"sub": str(group_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_group_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        group_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return group_id
