from pydantic import ValidationError

from app.ai_providers import gemini_client, groq_client
from app.schemas import LayoutSpec, ProviderEnum


class AIServiceError(Exception):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(detail)


async def generate_layout_spec(provider: ProviderEnum, prompt: str, api_key: str) -> LayoutSpec:
    try:
        if provider == ProviderEnum.groq:
            raw_spec = await groq_client.generate_layout_spec(prompt=prompt, api_key=api_key)
        elif provider == ProviderEnum.gemini:
            raw_spec = await gemini_client.generate_layout_spec(prompt=prompt, api_key=api_key)
        else:
            raise AIServiceError('PROVIDER_NOT_SUPPORTED', 'Unsupported provider')
    except (groq_client.ProviderAuthError, gemini_client.ProviderAuthError) as exc:
        raise AIServiceError('KEY_EXPIRED', str(exc)) from exc
    except (groq_client.ProviderRequestError, gemini_client.ProviderRequestError) as exc:
        raise AIServiceError('PROVIDER_API_ERROR', str(exc)) from exc

    try:
        return LayoutSpec.model_validate(raw_spec)
    except ValidationError as exc:
        raise AIServiceError('INVALID_JSON_RESPONSE', 'Provider response did not match expected schema') from exc
