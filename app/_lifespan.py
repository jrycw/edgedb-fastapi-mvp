from __future__ import annotations

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import FastAPI


@svcs.fastapi.lifespan
async def lifespan(app: FastAPI, registry: svcs.Registry):
    async_client = edgedb.create_async_client()

    async def setup_edgedb():
        return await async_client.ensure_connected()

    async def shutdown_edgedb():
        await async_client.aclose()

    async def ping_callable(client):
        return await client.query("select 1;")

    registry.register_factory(
        AsyncIOClient,
        setup_edgedb,
        on_registry_close=shutdown_edgedb,
        ping=ping_callable,
    )
    yield


# @svcs.fastapi.lifespan
# async def tx_lifespan(app: FastAPI, registry: svcs.Registry):
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
