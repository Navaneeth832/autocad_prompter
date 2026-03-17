from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProviderEnum(str, Enum):
    groq = 'groq'
    gemini = 'gemini'


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=10)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class APIKeyUpsertRequest(BaseModel):
    provider: ProviderEnum
    api_key: str = Field(min_length=10)


class APIKeyDeleteRequest(BaseModel):
    provider: ProviderEnum


class APIKeyStatusItem(BaseModel):
    provider: ProviderEnum
    configured: bool
    updated_at: datetime | None = None


class APIKeyStatusResponse(BaseModel):
    keys: list[APIKeyStatusItem]


class GenerateLayoutRequest(BaseModel):
    provider: ProviderEnum
    prompt: str = Field(min_length=5, max_length=4000)


class LayoutSpecItem(BaseModel):
    wall: str
    position: float


class LayoutSpec(BaseModel):
    width: float
    height: float
    doors: list[LayoutSpecItem] = []
    windows: list[LayoutSpecItem] = []


class GeometryResponse(BaseModel):
    walls: list[list[float]]
    doors: list[list[float]]
    windows: list[list[float]]


class GenerateLayoutResponse(BaseModel):
    spec: LayoutSpec
    geometry: GeometryResponse


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
