from sqlalchemy.orm import Session
from fastapi import Request


def get_db(request: Request) -> Session:
    return request.state.db
