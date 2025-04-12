from fastapi import APIRouter
from api.services.price_fetcher import get_gold_price, get_coin_price, get_last_updated

router = APIRouter()


@router.get("/gold")
async def gold_price():
    return {"data": get_gold_price(), "last_updated": get_last_updated()}


@router.get("/coin")
async def coin_price():
    return {"data": get_coin_price(), "last_updated": get_last_updated()}
