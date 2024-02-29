import datetime

from pydantic import BaseModel, Field, field_validator

from .models import EventBase, UserCreate

"""
Q: Why using forms instead of models?
A: 
* Can add more custom annotations and validators.
* Frontend might provide more information than backend(like current name in detailview), 
  so we don't need as many fields as backend requested.
* In order to utilize the FastUI UI widget, the schema needs to be assigned in forms.
* field rendering order.
* default could None for form.
* models => FastAPI, forms => FastUI.

Q: When do we need the model for the frontend?
A: 
* While displaying something like listview or detailview.
"""


class UserCreationForm(UserCreate):
    pass


class UserUpdateForm(BaseModel):
    """
    We don't inherit `UserCreationForm`, since we know the `name` already from frontend already.
    """

    new_name: str = Field(
        title="New Username", description="max length: 50", max_length=50
    )

    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        return v.strip()


################################
# Event
################################
class EventCreationForm(EventBase):
    """
    By using `datetime.datetime` for `schedule`, we can get the UI Widget
    """

    host_name: str = Field(
        title="Hostname",
        description="max length: 50 (This will create a new User if not found)",
        max_length=50,
    )
    address: str | None = None
    schedule: datetime.datetime | None = None

    @field_validator("host_name")
    @classmethod
    def validate_host_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: datetime.datetime | None) -> datetime.datetime | None:
        """Coercing timezone info"""
        if v is not None:
            v = v.astimezone(datetime.timezone.utc)
        return v


class EventUpdateForm(BaseModel):
    new_name: str | None = Field(
        default=None, title="New Eventname", description="max length: 50", max_length=50
    )
    host_name: str | None = Field(
        default=None,
        title="Hostname",
        description="max length: 50 (This will create a new User if not found)",
        max_length=50,
    )
    address: str | None = None
    schedule: datetime.datetime | None = None

    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("host_name")
    @classmethod
    def validate_host_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: datetime.datetime | None) -> datetime.datetime | None:
        """Coercing timezone info"""
        if v is not None:
            v = v.astimezone(datetime.timezone.utc)
        return v
