from .urls import prices
from fastapi import APIRouter

router = APIRouter()

# Include the tgju prices router
router.include_router(prices.router, prefix="/tgju/prices", tags=["tgju"])
