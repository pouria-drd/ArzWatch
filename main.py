import uvicorn
from fastapi import FastAPI
from api.routes import prices

app = FastAPI(title="ArzWatch API")

# Register routes
app.include_router(prices.router, prefix="/prices")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
