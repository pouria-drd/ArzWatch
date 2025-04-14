from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None, message: str = "success in processing", status_code: int = 200
):
    return JSONResponse(
        status_code=status_code,
        content={"status": "success", "message": message, "data": data},
    )


def created_response(
    data: Any = None, message: str = "created", status_code: int = 201
):
    return JSONResponse(
        status_code=status_code,
        content={"status": "success", "message": message, "data": data},
    )


def error_response(
    message: str = "error occurred",
    status_code: int = 400,
    errors: Optional[Any] = None,
):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message, "errors": errors},
    )


def not_found_response(message: str = "not found", status_code: int = 404):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def bad_request_response(message: str = "bad request", status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def unauthorized_response(message: str = "unauthorized", status_code: int = 401):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def forbidden_response(message: str = "forbidden", status_code: int = 403):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def internal_server_error_response(
    message: str = "internal server error", status_code: int = 500
):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def no_content_response(message: str = "no content", status_code: int = 204):
    return JSONResponse(
        status_code=status_code,
        content={"status": "success", "message": message},
    )
