from __future__ import annotations

from http import HTTPStatus


################################
# Good case
################################
def test_healthy(mocker, test_client, health_url):
    mocker.patch(
        "app.health._check_healthy",
        return_value=(["edgedb.asyncio_client.AsyncIOClient", "service_name_n"], []),
    )

    response = test_client.get(health_url)
    resp_json = response.json()
    resp_json_ok = resp_json["ok"]

    assert response.status_code == HTTPStatus.OK
    assert "edgedb.asyncio_client.AsyncIOClient" in resp_json_ok
    assert "service_name_n" in resp_json_ok


################################
# Bad case
################################
def test_not_healthy(mocker, test_client, health_url):
    mocker.patch(
        "app.health._check_healthy",
        return_value=(
            [],
            [
                {
                    "service_name_1": "Exceptions for service_name_1",
                    "service_name_2": "Exceptions for service_name_2",
                }
            ],
        ),
    )

    response = test_client.get(health_url)
    resp_json = response.json()
    resp_json_detail_error = resp_json["detail"]["error"]

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "Health check failed" in resp_json_detail_error
    assert "service_name_1" in resp_json_detail_error
    assert "Exceptions for service_name_1" in resp_json_detail_error
    assert "service_name_2" in resp_json_detail_error
    assert "Exceptions for service_name_2" in resp_json_detail_error
