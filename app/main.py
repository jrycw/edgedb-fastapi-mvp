from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import events, users

from ._lifespan import lifespan


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

    @app.get("/health_check", include_in_schema=False)
    async def health_check() -> dict[str, str]:
        return {"status": "Ok"}

    return app


app = make_app(lifespan)