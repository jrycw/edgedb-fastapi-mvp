from http import HTTPStatus

import pytest
from edgedb.asyncio_client import AsyncIOClient

from app.queries import prepare_dev_data_async_edgeql as prepare_dev_data_qry

from .factories import gen_event
from .lifespan import t_lifespan


################################
# Good case
################################
@pytest.mark.repeat(2)  # intentionally check the `schedule` field
@pytest.mark.parametrize("n", [0, 5, 50, 500])
def test_reset_dev_data(n, test_db_client, test_client, fixtures_url):
    event_dicts = [
        gen_event().model_dump(
            include={"id", "name", "address", "schedule", "host_name"}
        )
        for _ in range(n)
    ]

    test_db_client.query.return_value = [
        prepare_dev_data_qry.PrepareDevDataResult(**event_dict)
        for event_dict in event_dicts
    ]
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(fixtures_url, json={"n": n})
    resp_json_list = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json_list) == n

    for resp_json, event_dict in zip(resp_json_list, event_dicts):
        assert resp_json["id"] == event_dict["id"]
        assert resp_json["name"] == event_dict["name"]
        assert resp_json["address"] == event_dict["address"]
        assert resp_json["schedule"] == event_dict["schedule"]
        assert resp_json["host_name"] == event_dict["host_name"]
