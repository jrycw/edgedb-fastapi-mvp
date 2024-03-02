from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import Response
from httpx import AsyncClient

from .config import settings
from .forms import EventRepr, UserRepr


async def create_get_web_client():
    base_url = (
        f"{settings.backendschema}://{settings.backendhost}:{settings.backendport}"
    )
    async with AsyncClient(base_url=base_url) as client:
        yield client


async def create_post_put_delete_web_client():
    base_url = (
        f"{settings.backendschema}://{settings.backendhost}:{settings.backendport}"
    )
    async with AsyncClient(base_url=base_url) as client:
        csrftoken = (await client.get("/")).cookies.get("csrftoken")
        extra_headers = (
            {"headers": {"x-csrftoken": csrftoken}} if csrftoken is not None else {}
        )
        yield client, extra_headers


def _raise_for_status(response: Response, status_code: HTTPStatus = HTTPStatus.OK):
    resp_json = response.json()
    if response.status_code != status_code:
        raise HTTPException(
            status_code=response.status_code,
            detail=resp_json,
        )
    return resp_json


def _form_user_repr(resp_json: dict[str, str]) -> UserRepr:
    return UserRepr(**resp_json)


def _form_event_repr(resp_json: dict[str, str | dict[str, str] | None]) -> EventRepr:
    """
    `host_name = resp_json["host"]["name"]` works because host
    is required in the schema. If the rendering issue for
    `GoToEvent(url="/users/{host_name}/")` can be resolved,
    then we can do:

    host_name = None
    if host := resp_json["host"]:
        host_name = host.get("name")
    """
    host_name = resp_json["host"]["name"]  # since host is required in the schema
    resp_json.update(host_name=host_name)
    del resp_json["host"]
    return EventRepr(**resp_json)
