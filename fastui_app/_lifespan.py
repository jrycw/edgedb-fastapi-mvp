import svcs
from fastapi import FastAPI
from httpx import AsyncClient

from fastui_app.config import settings


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    # Web client(connect to backend)
    base_url = (
        f"{settings.backendschema}://{settings.backendhost}:{settings.backendport}"
    )
    client = AsyncClient(base_url=base_url)

    async def setup_httpx_client():
        yield client

    registry.register_factory(
        AsyncClient,
        setup_httpx_client,
    )

    yield

    await registry.aclose()
