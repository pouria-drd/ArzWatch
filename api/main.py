import uvicorn
from fastapi import FastAPI
from api.v1 import routes as v1_routes

app = FastAPI(title="ArzWatch API")

# Include v1 routes with prefix
app.include_router(v1_routes.router, prefix="/api/v1")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
