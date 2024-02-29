from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import Response

from .models import EventRepr


def _raise_for_status(response: Response, status_code: HTTPStatus = HTTPStatus.OK):
    resp_json = response.json()
    if response.status_code != status_code:
        raise HTTPException(
            status_code=response.status_code,
            detail=resp_json,
        )
    return resp_json


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
