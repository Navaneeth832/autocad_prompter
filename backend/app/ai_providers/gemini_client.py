import json

import httpx

from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = (
    'Return only valid JSON floor-plan schema: '
    '{"width": number, "height": number, "doors": [{"wall": "north|south|east|west", "position": number}], '
    '"windows": [{"wall": "north|south|east|west", "position": number}]}'
)


class ProviderAuthError(Exception):
    pass


class ProviderRequestError(Exception):
    pass


async def generate_layout_spec(prompt: str, api_key: str) -> dict:
    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0, 'response_mime_type': 'application/json'},
    }

    url = f'{settings.gemini_base_url}/models/{settings.gemini_model}:generateContent?key={api_key}'

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)

    if response.status_code in (401, 403):
        raise ProviderAuthError('Invalid or expired provider API key')
    if response.status_code >= 400:
        raise ProviderRequestError(f'Gemini API error: {response.status_code}')

    data = response.json()
    try:
        raw_content = data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ProviderRequestError('Invalid JSON response from Gemini') from exc
