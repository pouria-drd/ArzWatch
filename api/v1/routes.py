from . import prices
from fastapi import APIRouter

router = APIRouter()
router.include_router(prices.router, prefix="/prices")
