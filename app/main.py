import os
import sys

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

sys.path.append(os.getcwd())

from app import common, events, health, users
from app.config import settings
from app.lifespan import lifespan


def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[
        #     f"{settings.frontendschema}://{settings.frontendhost}:{settings.frontendport}"
        # ],
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(CSRFMiddleware, secret=settings.secret_csrf)

    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(health.router)
    app.include_router(common.router)

    return app


app = make_app(lifespan)

if __name__ == "__main__":
    print(f"Backend: {settings=}")
    uvicorn.run(
        "main:app",
        host=settings.backendhost,
        port=settings.backendport,
        reload=settings.backendreload,
    )
