import datetime
import random

from faker import Faker
from pydantic import BaseModel, Field

faker = Faker()


class TestAuditable(BaseModel):
    id: str = Field(default_factory=faker.uuid4)
    created_at: datetime.datetime = Field(
        default_factory=lambda: faker.date_time_this_month(
            tzinfo=datetime.timezone.utc
        ).replace(microsecond=random.randint(0, 999999))
    )


class TestUserData(TestAuditable):
    name: str = Field(default_factory=faker.name, max_length=50)


class TestUserDataWithnEvents(TestUserData):
    n_events: int = 0


def gen_event():
    """To address randomness, we need to make this special fixture-like function."""

    class TestEventData(TestAuditable):
        """
        The "address" and "schedule" fields are optional,
        meaning they can be set to `None`, and adding randomness
        may be beneficial for testing purposes.
        """

        name: str = Field(
            default_factory=lambda: faker.text(max_nb_chars=30), max_length=50
        )
        address: str | None = Field(
            default_factory=random.choice([faker.street_address, lambda: None])
        )

        # Interestingly, faker.date_time might fail occasionally in windows
        # due to not handle 1970/01/01 propriately
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

    return TestEventData()
