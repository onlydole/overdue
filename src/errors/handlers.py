"""FastAPI exception handlers for library incidents."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.errors.incidents import LibraryIncident, QuietHoursExceeded


def register_handlers(app: FastAPI) -> None:
    """Register exception handlers on the FastAPI application."""

    @app.exception_handler(LibraryIncident)
    async def library_incident_handler(request: Request, exc: LibraryIncident) -> JSONResponse:
        headers = {}
        if isinstance(exc, QuietHoursExceeded):
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "incident": {
                    "code": exc.code,
                    "detail": exc.detail,
                }
            },
            headers=headers,
        )
