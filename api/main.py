import uvicorn
from fastapi import FastAPI
from api.v1.routes import router as v1_router


base_api_path = "/api"

app = FastAPI(
    title="ArzWatch API",
    # openapi_url=None, Make it None to disable OpenAPI and Swagger UI in production
    version="0.0.1",
)

# Include v1 routes with prefix
app.include_router(v1_router, prefix="/v1")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
