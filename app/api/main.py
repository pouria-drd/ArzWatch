import uvicorn
from fastapi import FastAPI
from .routes.v1 import urls as v1_routes


base_api_path = "/api"

app = FastAPI(title="ArzWatch API")

# Include v1 routes with prefix
app.include_router(v1_routes.router, prefix=f"{base_api_path}/v1")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
