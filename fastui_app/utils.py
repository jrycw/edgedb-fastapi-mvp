from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import Response

from .forms import EventRepr, UserRepr


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
    Q: Why `host_name` is required in the schema?
    A: Since there exists a rendering issue for
    `GoToEvent(url="/users/{host_name}/")`.
    """
    return EventRepr(**resp_json)
