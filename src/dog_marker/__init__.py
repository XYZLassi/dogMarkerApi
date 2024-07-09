import functools
from contextlib import asynccontextmanager

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from pytz import utc

from .configs import Config
from .middlewares import register_middlewares
from .tasks import register_background_tasks
from .database.base import create_db

jobstores = {"default": MemoryJobStore()}


def create_app(config: Config = Config()) -> FastAPI:
    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=utc)

    app = FastAPI(title="DogMarker - API", lifespan=functools.partial(lifespan, scheduler=scheduler))

    session_local = create_db(app, config)

    register_middlewares(app, config, session_local)
    register_background_tasks(app, config, scheduler, session_local)

    from .api.v1 import api_v1

    app.mount("/v1", api_v1)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI, scheduler: AsyncIOScheduler):
    scheduler.start()
    yield
    scheduler.shutdown()
