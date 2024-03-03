from http import HTTPStatus

import edgedb
from edgedb.asyncio_client import AsyncIOClient

from app.queries import create_event_async_edgeql as create_event_qry
from app.queries import delete_event_async_edgeql as delete_event_qry
from app.queries import get_event_by_name_async_edgeql as get_event_by_name_qry
from app.queries import get_events_async_edgeql as get_events_qry
from app.queries import update_event_async_edgeql as update_event_qry

from .lifespan import t_lifespan


################################
# Good cases
################################
def test_get_event(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump()

    test_db_client.query_single.return_value = (
        get_event_by_name_qry.GetEventByNameResult(**return_event_dict)
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["created_at"] == return_event_dict["created_at"].isoformat()
    assert resp_json["address"] == return_event_dict["address"]
    assert resp_json["schedule"] == return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_get_events(gen_event, test_db_client, test_client, events_url):
    event1, event2 = gen_event(), gen_event()
    return_event1_dict, return_event2_dict = event1.model_dump(), event2.model_dump()

    test_db_client.query.return_value = [
        get_events_qry.GetEventsResult(**return_event1_dict),
        get_events_qry.GetEventsResult(**return_event2_dict),
    ]
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url)
    first_event, second_event = response.json()

    assert response.status_code == HTTPStatus.OK
    assert first_event["id"] == return_event1_dict["id"]
    assert first_event["name"] == return_event1_dict["name"]
    assert first_event["created_at"] == return_event1_dict["created_at"].isoformat()
    assert first_event["address"] == return_event1_dict["address"]
    assert first_event["schedule"] == return_event1_dict["schedule"]
    assert first_event["host_name"] == return_event1_dict["host_name"]

    assert second_event["id"] == return_event2_dict["id"]
    assert second_event["name"] == return_event2_dict["name"]
    assert second_event["created_at"] == return_event2_dict["created_at"].isoformat()
    assert second_event["address"] == return_event2_dict["address"]
    assert second_event["schedule"] == return_event2_dict["schedule"]
    assert second_event["host_name"] == return_event2_dict["host_name"]


def test_post_event1(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump(
        include={"id", "name", "address", "schedule", "host_name"}
    )

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **return_event_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["address"] == return_event_dict["address"]
    assert resp_json["schedule"] == return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_post_event2(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump(
        include={"id", "name", "schedule", "host_name"}
    )
    return_event_dict.update({"address": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **return_event_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["address"] is return_event_dict["address"]
    assert resp_json["schedule"] == return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_post_event3(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump(include={"id", "name", "address", "host_name"})
    return_event_dict.update({"schedule": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **return_event_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["address"] == return_event_dict["address"]
    assert resp_json["schedule"] is return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_post_event4(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump(include={"id", "name", "host_name"})
    return_event_dict.update({"address": None, "schedule": None})

    test_db_client.query_single.return_value = create_event_qry.CreateEventResult(
        **return_event_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["address"] is return_event_dict["address"]
    assert resp_json["schedule"] is return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_put_event(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    return_event_dict = event.model_dump(
        include={"id", "address", "schedule", "host_name"}
    ) | {"name": e_name_new}

    test_db_client.query_single.return_value = update_event_qry.UpdateEventResult(
        **return_event_dict
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
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == e_name_new
    assert resp_json["address"] == return_event_dict["address"]
    assert resp_json["schedule"] == return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


def test_delete_event(gen_event, test_db_client, test_client, events_url):
    event = gen_event()
    return_event_dict = event.model_dump(
        include={"id", "name", "address", "schedule", "host_name"}
    )

    test_db_client.query_single.return_value = delete_event_qry.DeleteEventResult(
        **return_event_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(
        events_url,
        params={"name": event.name},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == return_event_dict["id"]
    assert resp_json["name"] == return_event_dict["name"]
    assert resp_json["address"] == return_event_dict["address"]
    assert resp_json["schedule"] == return_event_dict["schedule"]
    assert resp_json["host_name"] == return_event_dict["host_name"]


################################
# Bad cases
################################


def test_get_event_not_found(gen_event, test_db_client, test_client, events_url):
    event = gen_event()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == f"Event '{event.name}' does not exist."


def test_post_event_bad_request1(gen_event, test_db_client, test_client, events_url):
    event = gen_event()

    test_db_client.query_single.side_effect = edgedb.errors.InvalidArgumentError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid datetime format" in resp_json["detail"]["error"]


def test_post_event_bad_request2(gen_event, test_db_client, test_client, events_url):
    event = gen_event()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(
        events_url,
        json={**event.model_dump(include={"name", "address", "schedule", "host_name"})},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Event name '{event.name}' already exists."


def test_put_event_bad_request1(gen_event, test_db_client, test_client, events_url):
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

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid datetime format" in resp_json["detail"]["error"]


def test_put_event_bad_request2(gen_event, test_db_client, test_client, events_url):
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

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Event name '{e_name_old}' already exists."


def test_put_event_internal_server_error(
    gen_event, test_db_client, test_client, events_url
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

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == f"Update event '{e_name_old}' failed."


def test_delete_event_internal_server_error(
    gen_event, test_db_client, test_client, events_url
):
    event = gen_event()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(
        events_url,
        params={"name": event.name},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == f"Delete event '{event.name}' failed."
