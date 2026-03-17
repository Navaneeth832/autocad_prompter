# PromptCAD Backend (FastAPI)

Production-oriented MVP backend for **PromptCAD – AI Floor Plan Generator**.

## Features
- Google OAuth sign-in (`POST /auth/google`)
- JWT-based auth for protected endpoints
- Encrypted BYOK API key management (Groq, Gemini)
- Provider abstraction layer for AI prompt-to-JSON generation
- Geometry engine converting room JSON into coordinate primitives
- Standardized error responses (`{"error": "..."}`)

## Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── apikeys.py
│   │   └── layout.py
│   ├── services/
│   │   ├── encryption.py
│   │   └── ai_service.py
│   ├── ai_providers/
│   │   ├── groq_client.py
│   │   └── gemini_client.py
│   ├── geometry/
│   │   └── layout_engine.py
│   └── utils/
│       ├── jwt_handler.py
│       ├── oauth_google.py
│       └── auth.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup
1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env file:
   ```bash
   cp .env.example .env
   ```
4. Update `.env` values.
5. Start app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Overview

### Authentication
- `POST /auth/google`
  - Body: `{ "id_token": "..." }`
  - Verifies Google token, upserts user, returns JWT.

### API Keys
- `POST /apikey/add`
- `POST /apikey/update`
- `GET /apikey/status`
- `DELETE /apikey/delete`

All protected with `Authorization: Bearer <jwt>`.

### Layout Generation
- `POST /generate-layout`
  - Body:
    ```json
    {
      "provider": "groq",
      "prompt": "Create a 10x8 room with a door on the south wall and a window on the north wall"
    }
    ```
  - Flow:
    1. Auth user from JWT
    2. Load + decrypt provider API key
    3. Send prompt to provider client
    4. Validate returned JSON schema
    5. Compute geometry points
    6. Return `{ spec, geometry }`

## Security Notes
- API keys are encrypted at rest using Fernet.
- API keys are decrypted only in-memory right before provider requests.
- Secrets are sourced from environment variables.
- API keys are never returned in API responses.

## Error Format

All controlled errors return:

```json
{
  "error": "ERROR_CODE"
}
```

Examples: `INVALID_TOKEN`, `KEY_NOT_FOUND`, `KEY_EXPIRED`, `PROVIDER_API_ERROR`, `INVALID_JSON_RESPONSE`.
