import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import FastAPI
from httpx import AsyncClient

from fastui_app.config import settings


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    # Web client(connect to backend)
    host = str(settings.backendhost).rstrip("/")  # any better ways?
    base_url = f"{host}:{settings.backendport}"
    client = AsyncClient(base_url=base_url)

    async def setup_httpx_client():
        yield client

    registry.register_factory(
        AsyncClient,
        setup_httpx_client,
    )
    if settings.frontenddebug:
        # EdgeDB client
        db_client = edgedb.create_async_client()

        async def setup_db_client():
            yield db_client

        async def ping_db_callable(_db_client):
            return await _db_client.query("select 1;")

        registry.register_factory(
            AsyncIOClient,
            setup_db_client,
            ping=ping_db_callable,
        )

    yield

    await registry.aclose()
