from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.routers import apikeys, auth, layout

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.app_debug)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and 'error' in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={'error': 'REQUEST_ERROR', 'detail': str(exc.detail)})


@app.get('/health')
def health() -> dict:
    return {'status': 'ok'}


app.include_router(auth.router)
app.include_router(apikeys.router)
app.include_router(layout.router)
