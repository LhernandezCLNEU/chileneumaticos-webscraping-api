from fastapi import FastAPI
from app.api.v1 import router as api_router

app = FastAPI(title="chileneumaticos-webscraping-api")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
