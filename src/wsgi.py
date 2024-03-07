import os

from starlette.middleware.cors import CORSMiddleware

from dog_marker import create_app
from dog_marker.configs import Config, DevelopConfig

env_config = os.environ.get("CONFIG", "Production")

config = Config()
if env_config == "Develop":
    config = DevelopConfig()

origins = ["*"]

app = create_app(config)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
