import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.settings import BASE_API_PATH
from api.v1.routes import router as v1_router
from api.services.schedulers.tgju_scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


base_api_path = BASE_API_PATH

app = FastAPI(
    title="ArzWatch API",
    # openapi_url=None, Make it None to disable OpenAPI and Swagger UI in production
    version="0.0.1",
    lifespan=lifespan,
    docs_url=f"{base_api_path}/docs",
    redoc_url=f"{base_api_path}/redoc",
)

# Include v1 routes with prefix
app.include_router(v1_router, prefix=f"{base_api_path}/v1")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
