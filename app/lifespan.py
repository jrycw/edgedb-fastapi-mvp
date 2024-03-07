import json
from functools import partial

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import FastAPI
from httpx import AsyncClient  # noqa: F401

from .config import settings
from .factories import gen_default_dev_data
from .queries import ping_db_async_edgeql as ping_db_qry
from .queries import set_default_dev_data_async_edgeql as set_default_dev_data_qry


async def _lifespan(app: FastAPI, registry: svcs.Registry, *, prefill: bool):
    # EdgeDB client
    db_client = edgedb.create_async_client()

    async def create_db_client():
        yield db_client

    async def ping_db_callable(_db_client):
        return ping_db_qry

    registry.register_factory(
        AsyncIOClient,
        create_db_client,
        ping=ping_db_callable,
    )

    if prefill:
        # Web client
        #     http_client = AsyncClient(
        #         base_url=f"{settings.backend_schema}://{settings.backend_host}:{settings.backend_port}"
        #     )

        #     async def create_http_client():
        #         yield http_client

        #     async def ping_http_callable(_http_client):
        #         return lambda _http_client: _http_client.get("/")

        #     registry.register_factory(
        #         AsyncClient, create_http_client, ping=ping_http_callable
        #     )

        await set_default_dev_data_qry.set_default_dev_data(
            db_client, data=json.dumps(gen_default_dev_data(n=5))
        )

    yield
    await registry.aclose()


def make_lifespan(*, prefill: bool):
    return svcs.fastapi.lifespan(partial(_lifespan, prefill=prefill))


lifespan = make_lifespan(prefill=settings.backend_prefill)

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
