from fastapi import Request

from dog_marker import Config


def get_config(request: Request) -> Config:
    return request.state.config
