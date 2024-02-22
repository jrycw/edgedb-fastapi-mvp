from __future__ import annotations  # noqa: F401

from http import HTTPStatus


################################
# Good case
################################
def test_healthy(mocker, test_client, health_url):
    mocker.patch(
        "app.health._check_healthy",
        return_value=(["edgedb.asyncio_client.AsyncIOClient"], []),
    )

    response = test_client.get(health_url)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["ok"] == ["edgedb.asyncio_client.AsyncIOClient"]


################################
# Bad case
################################
def test_not_healthy(mocker, test_client, health_url):
    mocker.patch(
        "app.health._check_healthy",
        return_value=(
            [],
            [{"edgedb.asyncio_client.AsyncIOClient": "Exceptions will be listed here"}],
        ),
    )

    response = test_client.get(health_url)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "edgedb.asyncio_client.AsyncIOClient" in resp_json["detail"]["error"]
