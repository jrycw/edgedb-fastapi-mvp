# import sys

# from starlette_csrf import CSRFMiddleware

# sys.path.append(os.getcwd())
# import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastui_app import common, events, users
from fastui_app.config import settings
from fastui_app.lifespan import lifespan
from fastui_app.logging import setup_logging
from fastui_app.middlewares import add_logging_middleware  # noqa: F401

setup_logging(
    json_logs=settings.frontend_log_json_format, log_level=settings.frontend_log_level
)


def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.middleware("http")(add_logging_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIdMiddleware)

    # app.add_middleware(CSRFMiddleware, secret=settings.secret_csrf)

    # order matters
    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(common.router)

    return app


app = make_app(lifespan)

# if __name__ == "__main__":
#     print(f"Frontend: {settings=}")
#     uvicorn.run(
#         "main:app",
#         host=settings.frontendhost,
#         port=settings.frontendport,
#         reload=settings.frontendreload,
#     )
