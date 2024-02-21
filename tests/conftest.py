from __future__ import annotations

import datetime
import random
import uuid

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app._lifespan import tx_lifespan
from app.main import app, make_app


@pytest.fixture
def users_url():
    yield "users"


@pytest.fixture
def events_url():
    yield "events"


@pytest.fixture
def faker():
    yield Faker()


@pytest.fixture
def gen_user(faker):
    class TestUserData(BaseModel):
        id: uuid.uuid4 = Field(default_factory=faker.uuid4)
        name: str = Field(default_factory=faker.name)
        extra_name: str = Field(default_factory=faker.name)
        created_at: datetime.datetime = Field(
            default_factory=lambda: faker.date_time().replace(
                microsecond=random.randint(0, 1000000)
            )
        )

    return lambda: TestUserData()


@pytest.fixture
def gen_event(faker):
    class TestEventData(BaseModel):
        id: uuid.uuid4 = Field(default_factory=faker.uuid4)
        name: str = Field(default_factory=lambda: faker.text(max_nb_chars=10))
        extra_name: str = Field(default_factory=lambda: faker.text(max_nb_chars=10))
        address: str = Field(default_factory=faker.street_address)
        schedule: datetime.datetime = Field(
            default_factory=lambda: faker.date_time().replace(
                microsecond=random.randint(0, 1000000)
            )
        )

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
