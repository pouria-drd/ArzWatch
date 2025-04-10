from fastapi import FastAPI
from api.routes import prices

app = FastAPI(title="ArzWatch API")

# Register routes
app.include_router(prices.router, prefix="/prices")
