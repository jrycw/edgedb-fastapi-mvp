from unittest.mock import Mock

import pytest
import structlog
from edgedb.asyncio_client import AsyncIOClient
from fastapi.testclient import TestClient
from structlog.testing import LogCapture

from app.main import make_app

from .lifespan import t_lifespan


@pytest.fixture(scope="session", autouse=True)
def users_url():
    yield "/users"


@pytest.fixture(scope="session", autouse=True)
def events_url():
    yield "/events"


@pytest.fixture(scope="session", autouse=True)
def health_url():
    yield "/healthy"


@pytest.fixture(scope="session", autouse=True)
def reset_default_dev():
    yield "/reset"


@pytest.fixture(scope="session", autouse=True)
def test_app():
    yield make_app(t_lifespan)


@pytest.fixture(scope="function", autouse=True)
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def test_db_client():
    yield Mock(spec_set=AsyncIOClient)


@pytest.fixture(scope="function")
def log_output():
    return LogCapture()


@pytest.fixture(scope="function", autouse=True)
def fixture_configure_structlog(log_output):
    structlog.configure(processors=[log_output])


# @pytest.fixture
# def tx_app():
#     yield make_app(tx_lifespan)


# @pytest.fixture
# def tx_test_client(tx_app):
#     with TestClient(tx_app) as client:
#         yield client
