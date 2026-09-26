from fastapi import FastAPI

from app.api.v1 import api_router

app = FastAPI(title="Wallet Service", version="0.1.0")

app.include_router(api_router)


@app.get("/", tags=["service"])
async def root():
    """Проверка, что сервис работает."""
    return {"status": "ok"}
