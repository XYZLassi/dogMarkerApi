__all__ = ["register_middlewares"]

import functools
from typing import Callable

from fastapi import FastAPI, Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from .configs import Config


def register_middlewares(app: FastAPI, config: Config, session_local: Callable[[], Session]):
    # noinspection PyTypeChecker
    app.add_middleware(BaseHTTPMiddleware, dispatch=functools.partial(config_middleware, config=config))
    # noinspection PyTypeChecker
    app.add_middleware(BaseHTTPMiddleware, dispatch=charset_middleware)
    # noinspection PyTypeChecker
    app.add_middleware(
        BaseHTTPMiddleware, dispatch=functools.partial(db_session_middleware, session_local=session_local)
    )


async def config_middleware(request: Request, call_next, config: Config | None = None):
    request.state.config = config
    response = await call_next(request)
    return response


async def charset_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    content_type: str = response.headers.get("content-type")

    if content_type and content_type.find("charset") == -1:
        content_type = f"{content_type}; charset={response.charset}"
        response.headers["content-type"] = content_type

    return response


async def db_session_middleware(request: Request, call_next, session_local: Callable[[], Session]):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = session_local()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response
