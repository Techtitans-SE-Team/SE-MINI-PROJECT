import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauth = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing authentication token",
                           headers={"WWW-Authenticate": "Bearer"})
    if creds is None:
        raise unauth
    try:
        payload = decode_access_token(creds.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauth
    user = db.get(User, user_id)
    if user is None:
        raise unauth
    return user


def require_roles(*roles: str):
    """Role-based access control dependency."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role_name not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
        return user
    return checker
