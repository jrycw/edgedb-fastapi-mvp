import svcs
from fastapi import FastAPI

from .clients import (
    BackendAsyncClient,
    FrontendGetAsyncClient,  # noqa: F401
    FrontendPostPutDeleteAsyncClient,  # noqa: F401
)
from .config import settings


async def _lifespan(app: FastAPI, registry: svcs.Registry):
    backend_client = BackendAsyncClient(
        base_url=f"{settings.backend_schema}://{settings.backend_host}:{settings.backend_port}"
    )

    async def creat_backend_client():
        """1 backend web client"""
        yield backend_client

    registry.register_factory(BackendAsyncClient, creat_backend_client)

    # frontend_get_client = FrontendGetAsyncClient(
    #     base_url=f"{settings.frontend_schema}://{settings.frontend_host}:{settings.frontend_port}"
    # )

    # async def create_frontend_get_client():
    #     """1 frontent web GET client"""
    #     yield frontend_get_client

    # registry.register_factory(
    #     FrontendGetAsyncClient,
    #     create_frontend_get_client,
    # )

    # async def create_frontend_post_put_delete_client():
    #     """For every post/put/delete, we request 1 specialized web client"""
    #     base_url = f"{settings.frontend_schema}://{settings.frontend_host}:{settings.frontend_port}"
    #     async with FrontendPostPutDeleteAsyncClient(base_url=base_url) as client:
    #         csrftoken = (await client.get("/")).cookies.get("csrftoken")
    #         # extra_headers = (
    #         #     {"headers": {"x-csrftoken": csrftoken}} if csrftoken is not None else {}
    #         # )
    #         csrftoken_dict = {"x-csrftoken": csrftoken} if csrftoken is not None else {}
    #         yield client, csrftoken_dict

    # registry.register_factory(
    #     FrontendPostPutDeleteAsyncClient,
    #     create_frontend_post_put_delete_client,
    # )

    yield

    await registry.aclose()


def make_lifespan():
    return svcs.fastapi.lifespan(_lifespan)


lifespan = make_lifespan()
