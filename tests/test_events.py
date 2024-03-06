from http import HTTPStatus

import edgedb
from edgedb.asyncio_client import AsyncIOClient

from app.queries import create_event_async_edgeql as create_event_qry
from app.queries import delete_event_async_edgeql as delete_event_qry
from app.queries import get_event_by_name_async_edgeql as get_event_by_name_qry
from app.queries import get_events_async_edgeql as get_events_qry
from app.queries import update_event_async_edgeql as update_event_qry

from .factories import gen_event
from .lifespan import t_lifespan
from .utils import assert_datetime_equal


################################
# Good cases
################################
def test_get_event(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump()

    test_db_client.query_single.return_value = (
        get_event_by_name_qry.GetEventByNameResult(**event_dic)
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert_datetime_equal(resp_json["created_at"], event_dic["created_at"])
    assert resp_json["address"] == event_dic["address"]
    assert resp_json["schedule"] == event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_get_events(test_db_client, test_client, events_url):
    event1, event2 = gen_event(), gen_event()
    event_dict1, event_dict2 = event1.model_dump(), event2.model_dump()

    test_db_client.query.return_value = [
        get_events_qry.GetEventsResult(**event_dict1),
        get_events_qry.GetEventsResult(**event_dict2),
    ]
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url)
    first_event, second_event = response.json()

    assert response.status_code == HTTPStatus.OK
    assert first_event["id"] == event_dict1["id"]
    assert first_event["name"] == event_dict1["name"]
    assert_datetime_equal(first_event["created_at"], event_dict1["created_at"])
    assert first_event["address"] == event_dict1["address"]
    assert first_event["schedule"] == event_dict1["schedule"]
    assert first_event["host_name"] == event_dict1["host_name"]

    assert second_event["id"] == event_dict2["id"]
    assert second_event["name"] == event_dict2["name"]
    assert_datetime_equal(second_event["created_at"], event_dict2["created_at"])
    assert second_event["address"] == event_dict2["address"]
    assert second_event["schedule"] == event_dict2["schedule"]
    assert second_event["host_name"] == event_dict2["host_name"]


def test_post_event1(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump(
        include={"id", "name", "address", "schedule", "host_name"}
    )

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert resp_json["address"] == event_dic["address"]
    assert resp_json["schedule"] == event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_post_event2(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump(include={"id", "name", "schedule", "host_name"})
    event_dic.update({"address": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert resp_json["address"] is event_dic["address"]
    assert resp_json["schedule"] == event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_post_event3(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump(include={"id", "name", "address", "host_name"})
    event_dic.update({"schedule": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert resp_json["address"] == event_dic["address"]
    assert resp_json["schedule"] is event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_post_event4(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump(include={"id", "name", "host_name"})
    event_dic.update({"address": None, "schedule": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert resp_json["address"] is event_dic["address"]
    assert resp_json["schedule"] is event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_put_event(test_db_client, test_client, events_url):
    event = gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    event_dic = event.model_dump(include={"id", "address", "schedule", "host_name"}) | {
        "name": e_name_new
    }

    test_db_client.query_single.return_value = update_event_qry.UpdateEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            **event.model_dump(include={"address", "schedule", "host_name"}),
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == e_name_new
    assert resp_json["address"] == event_dic["address"]
    assert resp_json["schedule"] == event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


def test_delete_event(test_db_client, test_client, events_url):
    event = gen_event()
    event_dic = event.model_dump(
        include={"id", "name", "address", "schedule", "host_name"}
    )

    test_db_client.query_single.return_value = delete_event_qry.DeleteEventResult(
        **event_dic
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(
        events_url,
        params={"name": event.name},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event_dic["id"]
    assert resp_json["name"] == event_dic["name"]
    assert resp_json["address"] == event_dic["address"]
    assert resp_json["schedule"] == event_dic["schedule"]
    assert resp_json["host_name"] == event_dic["host_name"]


################################
# Bad cases
################################


def test_get_event_not_found(test_db_client, test_client, events_url, log_output):
    event = gen_event()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()
    err_msg = f"Event '{event.name}' does not exist."

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_post_event_bad_request1(test_db_client, test_client, events_url, log_output):
    event = gen_event()

    test_db_client.query_single.side_effect = edgedb.errors.InvalidArgumentError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()
    first_log_ouput = log_output.entries[0]

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid datetime format" in resp_json["detail"]["error"]
    assert "Invalid datetime format" in first_log_ouput["event"]
    assert first_log_ouput["log_level"] == "warning"


def test_post_event_bad_request2(test_db_client, test_client, events_url, log_output):
    event = gen_event()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()
    err_msg = f"Event name '{event.name}' already exists."

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_put_event_bad_request1(test_db_client, test_client, events_url, log_output):
    event = gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"

    test_db_client.query_single.side_effect = edgedb.errors.InvalidArgumentError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            **event.model_dump(include={"address", "schedule", "host_name"}),
        },
    )
    resp_json = response.json()
    first_log_ouput = log_output.entries[0]

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid datetime format" in resp_json["detail"]["error"]
    assert "Invalid datetime format" in first_log_ouput["event"]
    assert first_log_ouput["log_level"] == "warning"


def test_put_event_bad_request2(test_db_client, test_client, events_url, log_output):
    event = gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            **event.model_dump(include={"address", "schedule", "host_name"}),
        },
    )
    resp_json = response.json()
    err_msg = f"Event name '{e_name_old}' already exists."

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_put_event_internal_server_error(
    test_db_client, test_client, events_url, log_output
):
    event = gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            **event.model_dump(include={"address", "schedule", "host_name"}),
        },
    )
    resp_json = response.json()
    err_msg = f"Update event '{e_name_old}' failed."

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_delete_event_internal_server_error(
    test_db_client, test_client, events_url, log_output
):
    event = gen_event()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(
        events_url,
        params={"name": event.name},
    )
    resp_json = response.json()
    err_msg = f"Delete event '{event.name}' failed."

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}
