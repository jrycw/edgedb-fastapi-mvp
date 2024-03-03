from http import HTTPStatus


def test_home(test_client):
    response = test_client.get("/")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json["message"] == "Hello World from FastAPI"
