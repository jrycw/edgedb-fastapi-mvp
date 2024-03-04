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
    name: str = Field(default_factory=faker.name, max_length=50)


class TestUserDataWithnEvents(TestUserData):
    n_events: int = 0


class TestEventData(TestAuditable):
    """
    The "address" and "schedule" fields are optional,
    meaning they can be set to `None`, and adding randomness
    may be beneficial for testing purposes.
    """

    name: str = Field(default_factory=lambda: faker.text(max_nb_chars=20))
    address: str = Field(
        default_factory=random.choice([faker.street_address, lambda: None])
    )
    schedule: str = Field(
        default_factory=random.choice(
            [
                lambda: faker.date_time()
                .replace(microsecond=random.randint(0, 1000000))
                .isoformat(),
                lambda: None,
            ]
        )
    )
    host_name: str = Field(default_factory=faker.name, max_length=50)
