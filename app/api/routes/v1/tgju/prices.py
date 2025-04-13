from fastapi import APIRouter
from app.api.services.tgju import (
    get_gold_price,
    get_coin_price,
    get_last_updated,
)

router = APIRouter()


@router.get("/gold")
def gold_price():
    """Get the gold price from the cache"""
    # Get the last updated time and gold price from the cache
    gold_price = get_gold_price()
    last_updated = get_last_updated()

    return {"data": gold_price, "last_updated": last_updated}


@router.get("/coin")
def coin_price():
    """Get the coin price from the cache"""
    # Get the last updated time and coin price from the cache
    coin_price = get_coin_price()
    last_updated = get_last_updated()

    return {"data": coin_price, "last_updated": last_updated}
