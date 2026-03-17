from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, GoogleAuthRequest
from app.utils.jwt_handler import create_access_token
from app.utils.oauth_google import GoogleAuthError, verify_google_id_token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/google', response_model=AuthResponse)
def google_login(payload: GoogleAuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        profile = verify_google_id_token(payload.id_token)
    except GoogleAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': 'INVALID_GOOGLE_TOKEN'}) from exc

    user = db.query(User).filter(User.email == profile['email']).first()
    if not user:
        user = User(email=profile['email'], name=profile['name'])
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user_id=user.id, email=user.email)
    return AuthResponse(access_token=access_token)

@router.post("/dev-login", response_model=AuthResponse)
def dev_login(db: Session = Depends(get_db)) -> AuthResponse:
    # Create or get a test user
    user = db.query(User).filter(User.email == "dev@test.com").first()

    if not user:
        user = User(email="dev@test.com", name="Dev User")
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user_id=user.id, email=user.email)

    return AuthResponse(access_token=access_token)