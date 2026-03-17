from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'PromptCAD Backend'
    app_env: str = Field(default='development', alias='APP_ENV')
    app_debug: bool = Field(default=True, alias='APP_DEBUG')

    database_url: str = Field(alias='DATABASE_URL')

    jwt_secret_key: str = Field(alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')
    jwt_expire_minutes: int = Field(default=60 * 24, alias='JWT_EXPIRE_MINUTES')

    google_client_id: str = Field(alias='GOOGLE_CLIENT_ID')

    encryption_key: str = Field(alias='ENCRYPTION_KEY')

    groq_base_url: str = Field(default='https://api.groq.com/openai/v1', alias='GROQ_BASE_URL')
    groq_model: str = Field(default='llama-3.1-70b-versatile', alias='GROQ_MODEL')

    gemini_base_url: str = Field(default='https://generativelanguage.googleapis.com/v1beta', alias='GEMINI_BASE_URL')
    gemini_model: str = Field(default='gemini-1.5-flash', alias='GEMINI_MODEL')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
