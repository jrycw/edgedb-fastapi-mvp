import svcs
from fastapi import FastAPI
from httpx import AsyncClient

from .clients import PostPutDeleteAsyncClient
from .config import settings
from .utils import create_post_put_delete_web_client


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    # Web client(connect to backend)
    base_url = (
        f"{settings.backendschema}://{settings.backendhost}:{settings.backendport}"
    )
    client = AsyncClient(base_url=base_url)

    async def setup_httpx_client():
        """only 1 web client for GET"""
        yield client

    registry.register_factory(
        AsyncClient,
        setup_httpx_client,
    )

    registry.register_factory(
        PostPutDeleteAsyncClient, create_post_put_delete_web_client
    )

    yield

    await registry.aclose()
