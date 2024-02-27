from __future__ import annotations

from http import HTTPStatus

import edgedb
from edgedb.asyncio_client import AsyncIOClient

from app.queries import create_user_async_edgeql as create_user_qry
from app.queries import delete_user_async_edgeql as delete_user_qry
from app.queries import get_user_by_name_async_edgeql as get_user_by_name_qry
from app.queries import get_users_async_edgeql as get_users_qry
from app.queries import update_user_async_edgeql as update_users_qry

from .lifespan import t_lifespan


################################
# Good cases
################################
def test_get_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.return_value = get_user_by_name_qry.GetUserByNameResult(
        **user.model_dump(), n_events=0
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user.id
    assert resp_json["name"] == user.name
    assert resp_json["created_at"] == user.created_at.isoformat()


def test_get_users(gen_user, test_db_client, test_client, users_url):
    user1, user2 = gen_user(), gen_user()

    test_db_client.query.return_value = [
        get_users_qry.GetUsersResult(
            **user1.model_dump(include={"id", "name", "created_at"}), n_events=0
        ),
        get_users_qry.GetUsersResult(
            **user2.model_dump(include={"id", "name", "created_at"}), n_events=0
        ),
    ]
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url)
    first_user, second_user = response.json()

    assert response.status_code == HTTPStatus.OK
    assert first_user["id"] == user1.id
    assert first_user["name"] == user1.name
    assert first_user["created_at"] == user1.created_at.isoformat()

    assert second_user["id"] == user2.id
    assert second_user["name"] == user2.name
    assert second_user["created_at"] == user2.created_at.isoformat()


def test_post_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.return_value = create_user_qry.CreateUserResult(
        **user.model_dump()
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(users_url, json={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == user.id
    assert resp_json["name"] == user.name
    assert resp_json["created_at"] == user.created_at.isoformat()


def test_put_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"

    test_db_client.query_single.return_value = update_users_qry.UpdateUserResult(
        **user.model_dump(include={"id", "created_at"}), name=u_name_new
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url,
        json={"name": u_name_old, "new_name": u_name_new},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user.id
    assert resp_json["name"] == u_name_new
    assert resp_json["created_at"] == user.created_at.isoformat()


def test_delete_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.return_value = delete_user_qry.DeleteUserResult(
        **user.model_dump()
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user.id
    assert resp_json["name"] == user.name
    assert resp_json["created_at"] == user.created_at.isoformat()


################################
# Bad cases
################################
def test_get_user_not_found(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == f"Username '{user.name}' does not exist."


def test_post_user_bad_request(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(users_url, json={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Username '{user.name}' already exists."


def test_put_user_not_found(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url,
        json={"name": u_name_old, "new_name": u_name_new},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == f"User '{u_name_old}' was not found."


def test_put_user_bad_request(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url,
        json={"name": u_name_old, "new_name": u_name_new},
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == f"Username '{u_name_old}' already exists."


def test_delete_user_not_found(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == f"User '{ user.name}' was not found."


def test_delete_user_bad_request(gen_user, test_db_client, test_client, users_url):
    user = gen_user()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == "User attached to an event. Cannot delete."
