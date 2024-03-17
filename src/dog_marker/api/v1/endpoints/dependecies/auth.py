from fastapi.security import HTTPBearer, HTTPBasicCredentials, HTTPBasic, HTTPAuthorizationCredentials
from fastapi import Request, Depends, HTTPException

from dog_marker import Config
from .config import get_config

basic_auth = HTTPBasic()
bearer_auth = HTTPBearer(auto_error=False)


async def authenticate_app(
    request: Request,
    config: Config = Depends(get_config),
    basic: HTTPBasicCredentials = Depends(bearer_auth),
    bearer: HTTPAuthorizationCredentials = Depends(bearer_auth),
) -> None:
    auth_header = request.headers.get("Authorization")
    if config.APP_TOKEN and not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")
    elif config.APP_TOKEN and auth_header:
        token = auth_header.removeprefix("Bearer ")
        if token != config.APP_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")

    return
