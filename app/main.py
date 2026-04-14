from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings
import logging

app = FastAPI(title="chileneumaticos-webscraping-api")

# CORS - allow local dev client origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Warn at startup if SSL verification is disabled
if settings.SKIP_SSL_VERIFY:
    logging.getLogger("uvicorn.warning").warning(
        "SKIP_SSL_VERIFY is enabled — SSL verification is disabled. Do NOT enable in production."
    )


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
