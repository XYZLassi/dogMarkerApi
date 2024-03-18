__all__ = ["api_v1"]

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .endpoints.entries import router as router_entries
from .endpoints.user_entries import router as router_user_entries
from dog_marker.database.errors import DbNotFoundError
from .errors import NotAuthorizedError

version = "0.2"
title = "dogMarker - API v1"
api_v1 = FastAPI(title=title, version=version)

api_v1.include_router(router_entries, tags=["Entry"], prefix="/entries")
api_v1.include_router(router_user_entries, tags=["Entry"], prefix="/user")


@api_v1.exception_handler(NotAuthorizedError)
async def not_authorized_exception_handler(request: Request, exc: NotAuthorizedError):
    return JSONResponse(
        status_code=401,
        content={"message": "Not enough privileges."},
    )


@api_v1.exception_handler(DbNotFoundError)
async def db_not_found_exception_handler(request: Request, exc: DbNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": exc.msg},
    )
