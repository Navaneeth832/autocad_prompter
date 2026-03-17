from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import APIKey, User
from app.schemas import (
    APIKeyDeleteRequest,
    APIKeyStatusItem,
    APIKeyStatusResponse,
    APIKeyUpsertRequest,
    ProviderEnum,
)
from app.services.encryption import encrypt_api_key
from app.utils.auth import get_current_user

router = APIRouter(prefix='/apikey', tags=['apikey'])


@router.post('/add')
def add_api_key(
    payload: APIKeyUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    existing = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.provider == payload.provider.value)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail={'error': 'KEY_ALREADY_EXISTS'})

    record = APIKey(
        user_id=current_user.id,
        provider=payload.provider.value,
        encrypted_key=encrypt_api_key(payload.api_key),
    )
    db.add(record)
    db.commit()

    return {'status': 'ok'}


@router.post('/update')
def update_api_key(
    payload: APIKeyUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    existing = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.provider == payload.provider.value)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail={'error': 'KEY_NOT_FOUND'})

    existing.encrypted_key = encrypt_api_key(payload.api_key)
    existing.updated_at = datetime.utcnow()
    db.add(existing)
    db.commit()

    return {'status': 'ok'}


@router.get('/status', response_model=APIKeyStatusResponse)
def api_key_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIKeyStatusResponse:
    rows = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    indexed = {row.provider: row for row in rows}

    keys = []
    for provider in ProviderEnum:
        record = indexed.get(provider.value)
        keys.append(
            APIKeyStatusItem(
                provider=provider,
                configured=record is not None,
                updated_at=record.updated_at if record else None,
            )
        )
    return APIKeyStatusResponse(keys=keys)


@router.delete('/delete')
def delete_api_key(
    payload: APIKeyDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    existing = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.provider == payload.provider.value)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail={'error': 'KEY_NOT_FOUND'})

    db.delete(existing)
    db.commit()
    return {'status': 'ok'}
