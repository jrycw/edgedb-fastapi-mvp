import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import FastAPI
from httpx import AsyncClient

from .config import settings


async def _lifespan(app: FastAPI, registry: svcs.Registry, need_fastui: bool):
    # EdgeDB client
    db_client = edgedb.create_async_client()

    async def setup_edgedb():
        return await db_client.ensure_connected()

    async def shutdown_edgedb():
        await db_client.aclose()

    async def ping_callable(_db_client):
        return await _db_client.query("select 1;")

    registry.register_factory(
        AsyncIOClient,
        setup_edgedb,
        on_registry_close=shutdown_edgedb,
        ping=ping_callable,
    )

    if need_fastui:
        # Web client
        host = str(settings.host).rstrip("/")  # any better ways?
        base_url = f"{host}:{settings.port}"
        client = AsyncClient(base_url=base_url)

        async def setup_httpx():
            yield client

        async def shutdown_httpx():
            await client.aclose()

        registry.register_factory(
            AsyncClient,
            setup_httpx,
            on_registry_close=shutdown_httpx,
        )

    yield


################################
# Need to modify _tx_lifespan
################################
# @svcs.fastapi.lifespan
# async def _tx_lifespan(app: FastAPI, registry: svcs.Registry):
#     async_client = edgedb.create_async_client()

#     async def tx_setup_edgedb():
#         await async_client.ensure_connected()
#         async for tx in async_client.with_retry_options(
#             edgedb.RetryOptions(0)
#         ).transaction():
#             async with tx:
#                 yield tx
#                 break

#     async def tx_shutdown_edgedb():
#         await async_client.aclose()

#     async def ping_callable(client):
#         return await client.query("select 1;")

#     registry.register_factory(
#         AsyncIOClient,
#         tx_setup_edgedb,
#         on_registry_close=tx_shutdown_edgedb,
#         ping=ping_callable,
#     )

#     yield
