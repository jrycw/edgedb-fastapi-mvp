from __future__ import annotations

import json
from http import HTTPStatus

from fastapi.responses import JSONResponse


################################
# Good case
################################
def test_healthy(mocker, health_url):
    expected_response = {
        "content": {"ok": ["edgedb.asyncio_client.AsyncIOClient"], "failing": []},
    }
    mocked_get = mocker.patch(
        "fastapi.testclient.TestClient.get",
        return_value=JSONResponse(content=expected_response, status_code=HTTPStatus.OK),
    )

    response = mocked_get(health_url)
    resp_json = json.loads(response.body)

    assert response.status_code == HTTPStatus.OK
    assert resp_json["content"]["ok"] == ["edgedb.asyncio_client.AsyncIOClient"]
    assert resp_json["content"]["failing"] == []


################################
# Bad case
################################
def test_not_healthy(mocker, health_url):
    expected_response = {
        "content": {
            "ok": [],
            "failing": [
                {
                    "edgedb.asyncio_client.AsyncIOClient": "Exceptions will be listed here"
                }
            ],
        },
    }
    mocked_get = mocker.patch(
        "fastapi.testclient.TestClient.get",
        return_value=JSONResponse(
            content=expected_response, status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        ),
    )

    response = mocked_get(health_url)
    resp_json = json.loads(response.body)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["content"]["ok"] == []
    assert resp_json["content"]["failing"] == [
        {"edgedb.asyncio_client.AsyncIOClient": "Exceptions will be listed here"}
    ]
