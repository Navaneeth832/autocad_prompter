from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.geometry.layout_engine import GeometryError, build_geometry
from app.models import APIKey, User
from app.schemas import GenerateLayoutRequest, GenerateLayoutResponse
from app.services.ai_service import AIServiceError, generate_layout_spec
from app.services.encryption import DecryptionError, decrypt_api_key
from app.utils.auth import get_current_user

router = APIRouter(tags=['layout'])


@router.post('/generate-layout', response_model=GenerateLayoutResponse)
async def generate_layout(
    payload: GenerateLayoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerateLayoutResponse:
    key_record = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.provider == payload.provider.value)
        .first()
    )
    if not key_record:
        raise HTTPException(status_code=404, detail={'error': 'KEY_NOT_FOUND'})

    try:
        raw_api_key = decrypt_api_key(key_record.encrypted_key)
    except DecryptionError as exc:
        raise HTTPException(status_code=500, detail={'error': 'KEY_DECRYPTION_FAILED'}) from exc

    try:
        spec = await generate_layout_spec(provider=payload.provider, prompt=payload.prompt, api_key=raw_api_key)
    except AIServiceError as exc:
        raise HTTPException(status_code=400, detail={'error': exc.code}) from exc

    try:
        geometry = build_geometry(spec)
    except GeometryError as exc:
        raise HTTPException(status_code=422, detail={'error': 'INVALID_LAYOUT_SPEC'}) from exc

    return GenerateLayoutResponse(spec=spec, geometry=geometry)
