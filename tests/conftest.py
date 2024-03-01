from __future__ import annotations

from unittest.mock import Mock

import pytest
from edgedb.asyncio_client import AsyncIOClient
from fastapi.testclient import TestClient

from app.main import make_app

from .factories import TestEventData, TestUserData, TestUserDataWithnEvents
from .lifespan import t_lifespan


@pytest.fixture
def users_url():
    yield "users"


@pytest.fixture
def events_url():
    yield "events"


@pytest.fixture
def health_url():
    yield "healthy"


@pytest.fixture
def gen_user():
    return lambda: TestUserData()


@pytest.fixture
def gen_user_with_n_event():
    return lambda: TestUserDataWithnEvents()


@pytest.fixture
def gen_event():
    return lambda: TestEventData()


@pytest.fixture(scope="session", autouse=True)
def test_app():
    """request 1 app(1 EdgeDB client) is enough per session"""
    yield make_app(t_lifespan)


@pytest.fixture(scope="session", autouse=True)
def test_client(test_app):
    """request 1 web client is enough per session"""
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def test_db_client():
    yield Mock(spec_set=AsyncIOClient)


# @pytest.fixture
# def tx_app():
#     yield make_app(tx_lifespan)


# @pytest.fixture
# def tx_test_client(tx_app):
#     with TestClient(tx_app) as client:
#         yield client
