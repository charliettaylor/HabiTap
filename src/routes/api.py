from fastapi import APIRouter
from src.routes import entries, habits

router = APIRouter()
router.include_router(entries.router)
router.include_router(habits.router)
