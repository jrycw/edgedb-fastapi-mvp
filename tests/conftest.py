from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app._lifespan import tx_lifespan
from app.main import app, make_app

from .factories import TestEventData, TestUserData


@pytest.fixture
def users_url():
    yield "users"


@pytest.fixture
def events_url():
    yield "events"


@pytest.fixture
def gen_user():
    return lambda: TestUserData()


@pytest.fixture
def gen_event():
    return lambda: TestEventData()


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def tx_app():
    yield make_app(tx_lifespan)


@pytest.fixture
def tx_test_client(tx_app):
    with TestClient(tx_app) as client:
        yield client
