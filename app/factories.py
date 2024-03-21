import datetime
import random

from faker import Faker
from pydantic import BaseModel, Field

faker = Faker()


def gen_event():
    """To address randomness, we need to make this special fixture-like function."""

    class FakeEventData(BaseModel):
        """
        The fields `address` and `schedule` are optional, allowing them to be set as `None`.
        Introducing randomness could be advantageous for testing.
        """

        name: str = Field(
            default_factory=lambda: faker.text(max_nb_chars=30), max_length=50
        )
        address: str | None = Field(
            default_factory=random.choice([faker.street_address, lambda: None])
        )
        schedule: str | None = Field(
            default_factory=random.choice(
                [
                    lambda: faker.future_datetime(tzinfo=datetime.timezone.utc)
                    .replace(microsecond=random.randint(0, 999999))
                    .isoformat(),
                    lambda: None,
                ]
            )
        )
        host_name: str = Field(default_factory=faker.name, max_length=50)

    return FakeEventData()


def gen_default_dev_data(n):
    return [
        gen_event().model_dump(include={"name", "address", "schedule", "host_name"})
        for _ in range(n)
    ]
