# import sys  # noqa: F401
# sys.path.append(os.getcwd())
# import uvicorn  # noqa: F401

import httpx  # noqa: F401
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import common, dev_reset, events, health, users  # noqa: F401
from app.config import settings
from app.lifespan import lifespan
from app.logging import setup_logging
from app.middlewares import add_logging_middleware  # noqa: F401

setup_logging(
    json_logs=settings.backend_log_json_format, log_level=settings.backend_log_level
)


def make_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.middleware("http")(add_logging_middleware)
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
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(health.router)
    app.include_router(common.router)
    app.include_router(dev_reset.router)

    # base_url = f"{settings.backend_schema}://{settings.backend_host}:{settings.backend_port}"
    # with httpx.Client(base_url=base_url) as client:
    #     r = client.post("/fixtures", json={})
    #     print(f"{r=}")

    return app


app = make_app(lifespan)


# if __name__ == "__main__":
#     print(f"Backend: {settings=}")
#     uvicorn.run(
#         "main:app",
#         host=settings.backendhost,
#         port=settings.backendport,
#         reload=settings.backendreload,
#     )
