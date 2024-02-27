import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import FastAPI


async def _lifespan(app: FastAPI, registry: svcs.Registry):
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
