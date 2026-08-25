"""Session handling: mint and verify our own JWTs, and expose them as a
FastAPI dependency.

The previous scheme handed the raw Google access token to the browser in a URL
query string and trusted a JS-readable cookie. This replaces both: the token
never leaves the server except as an HttpOnly cookie, and every protected
endpoint verifies it server-side.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, Response, status
from jose import JWTError, jwt

import config


class SessionUser:
    """The authenticated caller, as reconstructed from a verified token."""

    def __init__(self, email: str, name: str, picture: str, uid: str):
        self.email = email
        self.name = name
        self.picture = picture
        self.uid = uid

    def as_dict(self) -> dict:
        return {
            "id": self.uid,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
        }


def create_session_token(*, email: str, name: str, picture: str, uid: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "name": name,
        "picture": picture,
        "uid": uid,
        "iat": now,
        "exp": now + timedelta(seconds=config.SESSION_TTL_SECONDS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=token,
        max_age=config.SESSION_TTL_SECONDS,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=config.SESSION_COOKIE_NAME,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def _token_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get(config.SESSION_COOKIE_NAME)
    if token:
        return token
    # Fallback for non-browser clients that cannot hold cookies.
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip() or None
    return None


def get_current_user(request: Request) -> SessionUser:
    """Dependency: require a valid session, else 401."""
    token = _token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session payload",
        )

    return SessionUser(
        email=email,
        name=payload.get("name", ""),
        picture=payload.get("picture", ""),
        uid=payload.get("uid", ""),
    )


CurrentUser = Depends(get_current_user)
