import svcs
from fastapi import FastAPI

from .clients import (
    BackendAsyncClient,
    FrontendGetAsyncClient,
    FrontendPostPutDeleteAsyncClient,
)
from .config import settings


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    backend_client = BackendAsyncClient(
        base_url=f"{settings.backendschema}://{settings.backendhost}:{settings.backendport}"
    )

    async def creat_backend_client():
        """1 backend web client"""
        yield backend_client

    registry.register_factory(
        BackendAsyncClient,
        creat_backend_client,
    )

    front_get_client = BackendAsyncClient(
        base_url=f"{settings.frontendschema}://{settings.frontendhost}:{settings.frontendport}"
    )

    async def create_frontend_get_client():
        """1 frontent web GET client"""
        yield front_get_client

    registry.register_factory(
        FrontendGetAsyncClient,
        create_frontend_get_client,
    )

    async def create_frontend_post_put_delete_client():
        """For every post/put/delete, we request 1 specialized web client"""
        base_url = f"{settings.frontendschema}://{settings.frontendhost}:{settings.frontendport}"
        async with FrontendPostPutDeleteAsyncClient(base_url=base_url) as client:
            csrftoken = (await client.get("/")).cookies.get("csrftoken")
            # extra_headers = (
            #     {"headers": {"x-csrftoken": csrftoken}} if csrftoken is not None else {}
            # )
            csrftoken_dict = {"x-csrftoken": csrftoken} if csrftoken is not None else {}
            yield client, csrftoken_dict

    registry.register_factory(
        FrontendPostPutDeleteAsyncClient,
        create_frontend_post_put_delete_client,
    )

    yield

    await registry.aclose()
