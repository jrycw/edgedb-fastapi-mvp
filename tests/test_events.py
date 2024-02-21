from __future__ import annotations

from http import HTTPStatus

import edgedb
from edgedb.asyncio_client import AsyncIOClient

from app._lifespan import lifespan, tx_lifespan
from app.queries import create_event_async_edgeql as create_event_qry
from app.queries import delete_event_async_edgeql as delete_event_qry
from app.queries import (
    get_event_by_name_async_edgeql as get_event_by_name_qry,
)
from app.queries import get_events_async_edgeql as get_events_qry
from app.queries import update_event_async_edgeql as update_event_qry


################################
# Good cases
################################
def test_get_event(gen_event, gen_user, mocker, test_client, events_url):
    user, event = gen_user(), gen_event()
    host = get_event_by_name_qry.GetEventByNameResultHost(
        **user.model_dump(include={"id", "name"})
    )
    mocker.patch(
        "app.events.get_event_by_name_qry.get_event_by_name",
        return_value=get_event_by_name_qry.GetEventByNameResult(
            **event.model_dump(include={"id", "name", "address", "schedule"}),
            host=host,
        ),
    )
    lifespan.registry.register_value(AsyncIOClient, mocker)
    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event.id
    assert resp_json["name"] == event.name
    assert resp_json["address"] == event.address
    assert resp_json["schedule"] == event.schedule.isoformat()
    assert resp_json["host"]["id"] == user.id
    assert resp_json["host"]["name"] == user.name


def test_get_events(gen_event, gen_user, mocker, test_client, events_url):
    user1, user2 = gen_user(), gen_user()
    event1, event2 = gen_event(), gen_event()
    host1 = get_events_qry.GetEventsResultHost(
        **user1.model_dump(include={"id", "name"})
    )
    host2 = get_events_qry.GetEventsResultHost(
        **user2.model_dump(include={"id", "name"})
    )
    mocker.patch(
        "app.events.get_events_qry.get_events",
        return_value=[
            get_events_qry.GetEventsResult(
                **event1.model_dump(include={"id", "name", "address", "schedule"}),
                host=host1,
            ),
            get_events_qry.GetEventsResult(
                **event2.model_dump(include={"id", "name", "address", "schedule"}),
                host=host2,
            ),
        ],
    )
    lifespan.registry.register_value(AsyncIOClient, mocker)
    response = test_client.get(events_url)
    first_event, second_event = response.json()

    assert response.status_code == HTTPStatus.OK
    assert first_event["id"] == event1.id
    assert first_event["name"] == event1.name
    assert first_event["address"] == event1.address
    assert first_event["schedule"] == event1.schedule.isoformat()
    assert first_event["host"]["id"] == user1.id
    assert first_event["host"]["name"] == user1.name

    assert second_event["id"] == event2.id
    assert second_event["name"] == event2.name
    assert second_event["address"] == event2.address
    assert second_event["schedule"] == event2.schedule.isoformat()
    assert second_event["host"]["id"] == user2.id
    assert second_event["host"]["name"] == user2.name


def test_post_event(gen_event, gen_user, mocker, tx_test_client, events_url):
    user, event = gen_user(), gen_event()
    host = create_event_qry.CreateEventResultHost(
        **user.model_dump(include={"id", "name"})
    )
    mocker.patch(
        "app.events.create_event_qry.create_event",
        return_value=create_event_qry.CreateEventResult(
            **event.model_dump(include={"id", "name", "address", "schedule"}),
            host=host,
        ),
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.post(
        events_url,
        json={
            **event.model_dump(include={"name", "address"}),
            "schedule": event.schedule.isoformat(),
            "host_name": host.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == event.id
    assert resp_json["name"] == event.name
    assert resp_json["address"] == event.address
    assert resp_json["schedule"] == event.schedule.isoformat()
    assert resp_json["host"]["id"] == user.id
    assert resp_json["host"]["name"] == user.name


def test_put_event(gen_event, gen_user, mocker, tx_test_client, events_url):
    user, event = gen_user(), gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    host = update_event_qry.UpdateEventResultHost(
        **user.model_dump(include={"id", "name"})
    )
    mocker.patch(
        "app.events.update_event_qry.update_event",
        return_value=update_event_qry.UpdateEventResult(
            **event.model_dump(include={"id", "address", "schedule"}),
            name=e_name_new,
            host=host,
        ),
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            "address": event.address,
            "schedule": event.schedule.isoformat(),
            "host_name": host.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event.id
    assert resp_json["name"] == e_name_new
    assert resp_json["address"] == event.address
    assert resp_json["schedule"] == event.schedule.isoformat()
    assert resp_json["host"]["id"] == user.id
    assert resp_json["host"]["name"] == user.name


def test_delete_event(gen_event, gen_user, mocker, tx_test_client, events_url):
    user, event = gen_user(), gen_event()
    host = delete_event_qry.DeleteEventResultHost(
        **user.model_dump(include={"id", "name"})
    )
    mocker.patch(
        "app.events.delete_event_qry.delete_event",
        return_value=delete_event_qry.DeleteEventResult(
            **event.model_dump(include={"id", "name", "address", "schedule"}),
            host=host,
        ),
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.delete(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == event.id
    assert resp_json["name"] == event.name
    assert resp_json["address"] == event.address
    assert resp_json["schedule"] == event.schedule.isoformat()
    assert resp_json["host"]["id"] == user.id
    assert resp_json["host"]["name"] == user.name


################################
# Bad cases
################################


def test_get_event_not_found(gen_event, mocker, test_client, events_url):
    event = gen_event()
    mocker.patch(
        "app.events.get_event_by_name_qry.get_event_by_name", return_value=None
    )
    lifespan.registry.register_value(AsyncIOClient, mocker)
    response = test_client.get(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == f"Event '{event.name}' does not exist."


def test_post_event_bad_request1(
    gen_event, gen_user, mocker, tx_test_client, events_url
):
    user, event = gen_user(), gen_event()
    mocker.patch(
        "app.events.create_event_qry.create_event",
        side_effect=edgedb.errors.InvalidArgumentError,
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.post(
        events_url,
        json={
            **event.model_dump(include={"name", "address"}),
            "schedule": event.schedule.isoformat(),
            "host_name": user.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp_json["detail"]["error"]
        == "Invalid datetime format. "
        + "Datetime string must look like this: "
        + "'2010-12-27T23:59:59-07:00'"
    )


def test_post_event_bad_request2(
    gen_event, gen_user, mocker, tx_test_client, events_url
):
    user, event = gen_user(), gen_event()
    mocker.patch(
        "app.events.create_event_qry.create_event",
        side_effect=edgedb.errors.ConstraintViolationError,
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.post(
        events_url,
        json={
            **event.model_dump(include={"name", "address"}),
            "schedule": event.schedule.isoformat(),
            "host_name": user.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Event name '{event.name}' already exists."


def test_put_event_bad_request1(
    gen_event, gen_user, mocker, tx_test_client, events_url
):
    user, event = gen_user(), gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    mocker.patch(
        "app.events.update_event_qry.update_event",
        side_effect=edgedb.errors.InvalidArgumentError,
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            "address": event.address,
            "schedule": event.schedule.isoformat(),
            "host_name": user.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp_json["detail"]["error"]
        == "Invalid datetime format. "
        + "Datetime string must look like this: '2010-12-27T23:59:59-07:00'"
    )


def test_put_event_bad_request2(
    gen_event, gen_user, mocker, tx_test_client, events_url
):
    user, event = gen_user(), gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    mocker.patch(
        "app.events.update_event_qry.update_event",
        side_effect=edgedb.errors.ConstraintViolationError,
    )

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            "address": event.address,
            "schedule": event.schedule.isoformat(),
            "host_name": user.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Event name '{e_name_old}' already exists."


def test_put_event_internal_server_error(
    gen_event, gen_user, mocker, tx_test_client, events_url
):
    user, event = gen_user(), gen_event()
    e_name_old, e_name_new = event.name, f"{event.name}_new"
    mocker.patch("app.events.update_event_qry.update_event", return_value=None)

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.put(
        events_url,
        json={
            "name": e_name_old,
            "new_name": e_name_new,
            "address": event.address,
            "schedule": event.schedule.isoformat(),
            "host_name": user.name,
        },
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == f"Update event '{e_name_old}' failed."


def test_delete_event_internal_server_error(
    gen_event, mocker, tx_test_client, events_url
):
    event = gen_event()
    mocker.patch("app.events.delete_event_qry.delete_event", return_value=None)

    tx_lifespan.registry.register_value(AsyncIOClient, mocker)
    response = tx_test_client.delete(events_url, params={"name": event.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp_json["detail"]["error"] == f"Delete event '{event.name}' failed."
