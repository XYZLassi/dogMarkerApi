__all__ = ["register_background_tasks"]

import functools
from queue import Queue
from typing import Callable
from uuid import UUID

import requests
from apscheduler.schedulers.base import BaseScheduler
from bs4 import BeautifulSoup
from fastapi import FastAPI
from requests import session as requests_session
from sqlalchemy.orm import Session

from .configs import Config
from .database.cruds import EntryCRUD


def register_background_tasks(
    app: FastAPI, config: Config, scheduler: BaseScheduler, local_session: Callable[[], Session]
) -> Queue[Callable[[], None]]:
    task_queue: Queue[Callable[[], None]] = Queue()

    scheduler.add_job(
        functools.partial(job_execute_tasks, queue=task_queue), trigger="interval", seconds=10, max_instances=1
    )

    scheduler.add_job(
        functools.partial(job_find_deleted_entries, config=config, local_session=local_session, queue=task_queue),
        trigger="interval",
        seconds=10,
        max_instances=1,
    )

    return task_queue


def job_execute_tasks(queue: Queue[Callable[[], None]]):
    if not queue.empty():
        fn = queue.get()
        fn()


def job_find_deleted_entries(
    config: Config, local_session: Callable[[], Session], queue: Queue[Callable[[], None]]
) -> None:
    with local_session() as session:
        entry_crud = EntryCRUD(session)

        flow = entry_crud.query().map(entry_crud.filter_show_owner_deleted()).map(entry_crud.all())

        if flow.is_err():
            return  # Todo: LogError

        if not flow.value:  # Empty List
            return

        for entry in flow.value:
            fn_delete_entry = functools.partial(
                task_delete_entry,
                entry_id=entry.id,
                local_session=local_session,
                queue=queue,
            )
            queue.put(fn_delete_entry)


def task_delete_entry(entry_id: UUID, local_session: Callable[[], Session], queue: Queue[Callable[[], None]]) -> None:
    with local_session() as session:
        entry_crud = EntryCRUD(session)

        flow = entry_crud.get(entry_id)

        if flow.is_err():
            return  # Todo: LogError

        entry = flow.value

        if entry.image_infos:
            for images in entry.image_infos:
                fn_delete_image = functools.partial(task_delete_image, image_id=images.id, local_session=local_session)
                queue.put(fn_delete_image)
            return

        session.delete(entry)
        session.commit()
        return


def task_delete_image(image_id: int, local_session: Callable[[], Session]) -> None:
    with local_session() as session:
        entry_crud = EntryCRUD(session)

        flow = entry_crud.get_image(image_id)

        if flow.is_err():
            return  # Todo: LogError

        image = flow.value

        if image.image_path:
            check_response = requests.get(image.image_path)
            if check_response.status_code == 404:
                session.delete(image)
                session.commit()
                return

        if not image.image_delete_url:
            session.delete(image)
            session.commit()

        # Todo: Only for vgy.me
        with requests_session() as s:
            check_delete_response = s.get(image.image_delete_url)

            soup = BeautifulSoup(
                check_delete_response.text,
            )
            token = soup.find("input", {"name": "_token"}).attrs["value"]

            delete_data = {"confirm_delete": "1", "_token": token}

            s.post(image.image_delete_url, json=delete_data)

        return
