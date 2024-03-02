import os
import sys

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# from starlette_csrf import CSRFMiddleware

sys.path.append(os.getcwd())

from fastui_app import common, events, users  # noqa: F401
from fastui_app.config import settings
from fastui_app.lifespan import lifespan


def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(CSRFMiddleware, secret=settings.secret_csrf)

    # order matters
    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(common.router)

    return app


app = make_app(lifespan)

if __name__ == "__main__":
    print(f"Frontend: {settings=}")
    uvicorn.run(
        "main:app",
        host=settings.frontendhost,
        port=settings.frontendport,
        reload=settings.frontendreload,
    )
