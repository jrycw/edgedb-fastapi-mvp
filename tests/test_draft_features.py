from http import HTTPStatus

from edgedb.asyncio_client import AsyncIOClient

from .lifespan import t_lifespan


################################
# Good cases
################################
def test_search_users_ilike_all(test_db_client, test_client):
    search_user_ilike_url = "/users/search"
    return_value = ["Jerry", "Mike", "Julia", "David", "Paul"]
    test_db_client.query.return_value = return_value
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(search_user_ilike_url)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert set(resp_json) == set(return_value)


def test_search_users_ilike_filter(test_db_client, test_client):
    search_user_ilike_url = "/users/search"
    return_value = ["Jerry", "Julia"]
    test_db_client.query.return_value = return_value
    t_lifespan.registry.register_value(AsyncIOClient, test_db_client)

    response = test_client.get(search_user_ilike_url, params={"name": "j"})
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert set(resp_json) == set(return_value)
