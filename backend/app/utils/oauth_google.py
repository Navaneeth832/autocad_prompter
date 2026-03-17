from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import get_settings

settings = get_settings()


class GoogleAuthError(Exception):
    pass


def verify_google_id_token(token: str) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), settings.google_client_id)
    except Exception as exc:  # token verifier raises broad exceptions
        raise GoogleAuthError('Invalid Google token') from exc

    email = id_info.get('email')
    name = id_info.get('name') or email

    if not email:
        raise GoogleAuthError('Google token does not include an email')

    return {'email': email, 'name': name}
