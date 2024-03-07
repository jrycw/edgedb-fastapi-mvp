from http import HTTPStatus

import edgedb
import pytest
from edgedb.asyncio_client import AsyncIOClient

from app.queries import create_user_async_edgeql as create_user_qry
from app.queries import delete_user_async_edgeql as delete_user_qry
from app.queries import get_user_by_name_async_edgeql as get_user_by_name_qry
from app.queries import get_users_async_edgeql as get_users_qry
from app.queries import update_user_async_edgeql as update_users_qry

from .factories import TestUserData, TestUserDataWithnEvents
from .lifespan import t_lifespan
from .utils import assert_datetime_equal


################################
# Fixtures
################################
@pytest.fixture(scope="function")
def gen_user():
    return lambda: TestUserData()


@pytest.fixture(scope="function")
def gen_user_with_n_event():
    return lambda: TestUserDataWithnEvents()


################################
# Good cases
################################
def test_get_user(gen_user_with_n_event, test_db_client, test_client, users_url):
    user = gen_user_with_n_event()
    user_dict = user.model_dump()

    test_db_client.query_single.return_value = get_user_by_name_qry.GetUserByNameResult(
        **user_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user_dict["id"]
    assert resp_json["name"] == user_dict["name"]
    assert_datetime_equal(resp_json["created_at"], user_dict["created_at"])


def test_get_users(gen_user_with_n_event, test_db_client, test_client, users_url):
    user1, user2 = gen_user_with_n_event(), gen_user_with_n_event()
    user_dict1, user_dict2 = user1.model_dump(), user2.model_dump()

    test_db_client.query.return_value = [
        get_users_qry.GetUsersResult(**user_dict1),
        get_users_qry.GetUsersResult(**user_dict2),
    ]
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url)
    first_user, second_user = response.json()

    assert response.status_code == HTTPStatus.OK
    assert first_user["id"] == user_dict1["id"]
    assert first_user["name"] == user_dict1["name"]
    assert_datetime_equal(first_user["created_at"], user_dict1["created_at"])

    assert second_user["id"] == user_dict2["id"]
    assert second_user["name"] == user_dict2["name"]
    assert_datetime_equal(second_user["created_at"], user_dict2["created_at"])


def test_post_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    user_dict = user.model_dump()

    test_db_client.query_single.return_value = create_user_qry.CreateUserResult(
        **user_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(users_url, json={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp_json["id"] == user_dict["id"]
    assert resp_json["name"] == user_dict["name"]
    assert_datetime_equal(resp_json["created_at"], user_dict["created_at"])


def test_put_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"
    user_dict = user.model_dump(include={"id", "created_at"}) | {"name": u_name_new}

    test_db_client.query_single.return_value = update_users_qry.UpdateUserResult(
        **user_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url, json={"name": u_name_old, "new_name": u_name_new}
    )
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user_dict["id"]
    assert resp_json["name"] == u_name_new
    assert_datetime_equal(resp_json["created_at"], user_dict["created_at"])


def test_delete_user(gen_user, test_db_client, test_client, users_url):
    user = gen_user()
    user_dict = user.model_dump()

    test_db_client.query_single.return_value = delete_user_qry.DeleteUserResult(
        **user_dict
    )
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["id"] == user_dict["id"]
    assert resp_json["name"] == user_dict["name"]
    assert_datetime_equal(resp_json["created_at"], user_dict["created_at"])


################################
# Bad cases
################################
def test_get_user_not_found(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(users_url, params={"name": user.name})
    resp_json = response.json()
    err_msg = f"Username '{user.name}' does not exist."

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_post_user_bad_request(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.post(users_url, json={"name": user.name})
    resp_json = response.json()
    err_msg = f"Username '{user.name}' already exists."

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_put_user_not_found(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url, json={"name": u_name_old, "new_name": u_name_new}
    )
    resp_json = response.json()
    err_msg = f"User '{u_name_old}' was not found."

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_put_user_bad_request(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()
    u_name_old, u_name_new = user.name, f"{user.name}_new"

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.put(
        users_url, json={"name": u_name_old, "new_name": u_name_new}
    )
    resp_json = response.json()
    err_msg = f"Username '{u_name_old}' already exists."

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_delete_user_not_found(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()

    test_db_client.query_single.return_value = None
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()
    err_msg = f"User '{user.name}' was not found."

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}


def test_delete_user_bad_request(
    gen_user, test_db_client, test_client, users_url, log_output
):
    user = gen_user()

    test_db_client.query_single.side_effect = edgedb.errors.ConstraintViolationError
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.delete(users_url, params={"name": user.name})
    resp_json = response.json()
    err_msg = "User attached to an event. Cannot delete."

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert resp_json["detail"]["error"] == err_msg
    assert log_output.entries[0] == {"event": err_msg, "log_level": "warning"}
