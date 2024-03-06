__all__ = ["api_v1"]

from fastapi import FastAPI

from .endpoints.entries import router as router_entries
from .endpoints.user_entries import router as router_user_entries

version = "0.1.0"
title = "dogMarker - API v1"
api_v1 = FastAPI(title=title, version=version)

api_v1.include_router(router_entries, tags=["Entry"], prefix="/entries")
api_v1.include_router(router_user_entries, tags=["Entry"], prefix="/user")
