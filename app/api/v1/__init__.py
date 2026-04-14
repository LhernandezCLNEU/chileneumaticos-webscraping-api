from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .title_formats import router as title_formats_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(title_formats_router)
