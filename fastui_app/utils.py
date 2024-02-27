from http import HTTPStatus

from fastapi import HTTPException
from fastapi.responses import Response


def _raise_for_status(response: Response, status_code: HTTPStatus = HTTPStatus.OK):
    resp_json = response.json()
    if response.status_code != status_code:
        raise HTTPException(
            status_code=response.status_code,
            detail=resp_json,
        )
    return resp_json
