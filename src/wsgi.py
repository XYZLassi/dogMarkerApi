from starlette.middleware.cors import CORSMiddleware

from dog_marker import create_app

origins = ["*"]

app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
