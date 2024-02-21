from __future__ import annotations

import datetime
import random

from faker import Faker
from pydantic import BaseModel, Field

faker = Faker()


class TestAuditable(BaseModel):
    id: str = Field(default_factory=faker.uuid4)
    created_at: datetime.datetime = Field(
        default_factory=lambda: faker.date_time().replace(
            microsecond=random.randint(0, 1000000)
        )
    )


class TestUserData(TestAuditable):
    name: str = Field(default_factory=faker.name)


class TestEventData(TestAuditable):
    name: str = Field(default_factory=lambda: faker.text(max_nb_chars=10))
    address: str = Field(default_factory=faker.street_address)
    schedule: datetime.datetime = Field(
        default_factory=lambda: faker.date_time().replace(
            microsecond=random.randint(0, 1000000)
        )
    )
