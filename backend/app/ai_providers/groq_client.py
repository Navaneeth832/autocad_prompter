import json

import httpx

from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = (
    'You are a floor-plan parser. Convert user text into JSON only with schema: '
    '{"width": number, "height": number, "doors": [{"wall": "north|south|east|west", "position": number}], '
    '"windows": [{"wall": "north|south|east|west", "position": number}]}. '
    'No markdown, no prose.'
)


class ProviderAuthError(Exception):
    pass


class ProviderRequestError(Exception):
    pass


async def generate_layout_spec(prompt: str, api_key: str) -> dict:
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {
        'model': settings.groq_model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0,
        'response_format': {'type': 'json_object'},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f'{settings.groq_base_url}/chat/completions', json=payload, headers=headers)

    if response.status_code in (401, 403):
        raise ProviderAuthError('Invalid or expired provider API key')
    if response.status_code >= 400:
        raise ProviderRequestError(f'Groq API error: {response.status_code}')

    data = response.json()
    try:
        raw_content = data['choices'][0]['message']['content']
        return json.loads(raw_content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ProviderRequestError('Invalid JSON response from Groq') from exc
