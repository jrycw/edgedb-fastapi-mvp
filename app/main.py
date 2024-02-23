from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import events, health, users

from .config import settings
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

    if settings.need_fastui:
        from app.fastui import users as ui_users

        app.include_router(ui_users.router)

    return app


app = make_app(lifespan)
