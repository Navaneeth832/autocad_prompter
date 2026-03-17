from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


class InvalidTokenError(Exception):
    pass


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {'sub': str(user_id), 'email': email, 'exp': expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if 'sub' not in payload:
            raise InvalidTokenError('Token missing subject')
        return payload
    except JWTError as exc:
        raise InvalidTokenError('Invalid or expired token') from exc
