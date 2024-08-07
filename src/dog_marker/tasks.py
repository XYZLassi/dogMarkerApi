__all__ = ["register_background_tasks"]

import functools
import datetime
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
from .database.cruds import EntryCRUD, EntryImageCRUD


def register_background_tasks(
    app: FastAPI, config: Config, scheduler: BaseScheduler, local_session: Callable[[], Session]
) -> Queue[Callable[[], None]]:
    task_queue: Queue[Callable[[], None]] = Queue()

    scheduler.add_job(
        functools.partial(job_execute_tasks, queue=task_queue),
        trigger="interval",
        seconds=config.JOB_EXECUTE_INTERVAL_SECONDS,
        max_instances=1,
    )

    scheduler.add_job(
        functools.partial(job_find_deleted_entries, config=config, local_session=local_session, queue=task_queue),
        trigger="interval",
        seconds=config.JOB_CLEANUP_INTERVAL_SECONDS,
        max_instances=1,
    )

    scheduler.add_job(
        functools.partial(job_find_old_entries, config=config, local_session=local_session, queue=task_queue),
        trigger="interval",
        seconds=config.JOB_CLEANUP_INTERVAL_SECONDS,
        max_instances=1,
    )

    scheduler.add_job(
        functools.partial(job_check_images, config=config, local_session=local_session, queue=task_queue),
        trigger="interval",
        seconds=config.JOB_CLEANUP_INTERVAL_SECONDS,
        max_instances=1,
    )

    return task_queue


def job_execute_tasks(queue: Queue[Callable[[], None]]):
    if not queue.empty():
        fn = queue.get()
        fn()


def job_find_old_entries(
    config: Config, local_session: Callable[[], Session], queue: Queue[Callable[[], None]]
) -> None:
    with local_session() as session:
        entry_crud = EntryCRUD(session)
        time_diff = datetime.timedelta(days=config.DELETE_ENTRIES_AFTER_DAYS)
        older_than = datetime.datetime.utcnow() - time_diff

        flow = (
            entry_crud.query()
            .map(entry_crud.filter_marked_to_delete())
            .map(entry_crud.filter_older_than(older_than=older_than))
            .map(entry_crud.all())
        )

        if flow.is_err():
            return  # Todo: LogError

        for entry in flow.value:
            fn_delete_entry = functools.partial(
                task_delete_entry,
                entry_id=entry.id,
                local_session=local_session,
                queue=queue,
            )
            queue.put(fn_delete_entry)


def job_check_images(config: Config, local_session: Callable[[], Session], queue: Queue[Callable[[], None]]):
    with local_session() as session:
        entry_image_crud = EntryImageCRUD(session)
        flow = entry_image_crud.get_all()
        if flow.is_err():
            return  # Todo: LogError

        for images in flow.value:
            fn_check_image = functools.partial(
                task_check_image,
                image_id=images.id,
                local_session=local_session,
            )
            queue.put(fn_check_image)


def job_find_deleted_entries(
    config: Config, local_session: Callable[[], Session], queue: Queue[Callable[[], None]]
) -> None:
    with local_session() as session:
        entry_crud = EntryCRUD(session)

        older_than: datetime.datetime | None = None
        if config.DELETE_TRASH_ENTRIES_AFTER_MINUTES is not None and config.DELETE_TRASH_ENTRIES_AFTER_MINUTES >= 0:
            time_diff = datetime.timedelta(minutes=config.DELETE_TRASH_ENTRIES_AFTER_MINUTES)
            older_than = datetime.datetime.utcnow() - time_diff

        flow = entry_crud.query().map(entry_crud.filter_to_delete(older_than=older_than)).map(entry_crud.all())

        if flow.is_err():
            return  # Todo: LogError

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

        flow = entry_crud.get(entry_id).map(entry_crud.set_mark_to_delete()).map(entry_crud.commit())

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


def task_check_image(image_id: int, local_session: Callable[[], Session]):
    with local_session() as session:
        image_crud = EntryImageCRUD(session)
        flow = image_crud.get(image_id)

        if flow.is_err():
            return  # Todo: LogError

        image = flow.value

        if not image.image_path:
            session.delete(image)
            session.commit()
            return

        response = requests.get(image.image_path)
        if response.status_code == 404:
            session.delete(image)
            session.commit()
            return


def task_delete_image(image_id: int, local_session: Callable[[], Session]) -> None:
    with local_session() as session:
        image_crud = EntryImageCRUD(session)

        flow = image_crud.get(image_id)

        if flow.is_err():
            return  # Todo: LogError

        image = flow.value

        if not image.image_path or image.image_delete_url:
            session.delete(image)
            session.commit()

        check_response = requests.get(image.image_path)
        if check_response.status_code == 404:
            session.delete(image)
            session.commit()
            return

        # Todo: Only for vgy.me
        with requests_session() as s:
            check_delete_response = s.get(image.image_delete_url)
            assert check_delete_response.ok

            soup = BeautifulSoup(
                check_delete_response.text,
            )
            token = soup.find("input", {"name": "_token"}).attrs["value"]

            delete_data = {"confirm_delete": "1", "_token": token}

            delete_response = s.post(image.image_delete_url, json=delete_data)
            assert delete_response.ok

        check_response = requests.get(image.image_path)
        if check_response.status_code == 404:
            session.delete(image)
            session.commit()
            return
