from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import common, events, health, users

from .lifespan import lifespan


def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(health.router)
    app.include_router(common.router)

    return app


app = make_app(lifespan)
