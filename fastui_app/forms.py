import datetime

from pydantic import BaseModel, Field, field_validator
from zoneinfo import ZoneInfo

from .config import settings
from .models import EventFull, UserFull

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

################################
# Repr
################################
user_prefer_zoneinfo = ZoneInfo(settings.tz)


class DisplayAuditable:
    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: datetime.datetime) -> datetime.datetime:
        """This function decides how to render `Created_at`"""
        return v.astimezone(user_prefer_zoneinfo).replace(microsecond=0)


class UserRepr(UserFull, DisplayAuditable):
    pass


class EventRepr(EventFull, DisplayAuditable):
    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: str | None) -> str | None:
        """This function decides how to render `schedule`"""
        if v is not None:
            v = (
                datetime.datetime.fromisoformat(v)
                .astimezone(user_prefer_zoneinfo)
                .isoformat()
            )
        return v


################################
# User
################################


class UserNameCreationForm(BaseModel):
    name: str = Field(title="Username", description="max length: 50", max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()


class UserCreationForm(UserNameCreationForm):
    pass


class UserNewNameUpdateForm(BaseModel):
    new_name: str = Field(
        title="New Username", description="max length: 50", max_length=50
    )

    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        return v.strip()


class UserUpdateForm(UserNewNameUpdateForm):
    pass


################################
# Event
################################
class EventNameCreationForm(BaseModel):
    name: str = Field(title="Eventname", description="max length: 50", max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()


class EventHostNameCreationForm(BaseModel):
    host_name: str = Field(
        title="Hostname",
        description="max length: 50 (This will create a new User if not found)",
        max_length=50,
    )

    @field_validator("host_name")
    @classmethod
    def validate_host_name(cls, v: str) -> str:
        return v.strip()


class EventAddressCreationForm(BaseModel):
    address: str | None = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v


class EventScheduleCreationForm(BaseModel):
    """
    By using `datetime.datetime` for `schedule`, we can get the UI Widget
    """

    schedule: datetime.datetime | None = None

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: datetime.datetime | None) -> datetime.datetime | None:
        """Add timezone info"""
        if v is not None:
            v = v.astimezone(datetime.timezone.utc)
        return v


class EventCreationForm(
    EventScheduleCreationForm,
    EventAddressCreationForm,
    EventHostNameCreationForm,
    EventNameCreationForm,
):
    pass


class EventNewNameUpdateForm(BaseModel):
    new_name: str | None = Field(
        default=None, title="New Eventname", description="max length: 50", max_length=50
    )

    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v


class EvenHostNameUpdateForm(BaseModel):
    host_name: str | None = Field(
        default=None,
        title="Hostname",
        description="max length: 50 (This will create a new User if not found)",
        max_length=50,
    )

    @field_validator("host_name")
    @classmethod
    def validate_host_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v


class EvenAddressUpdateForm(BaseModel):
    address: str | None = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
        return v


class EventScheduleUpdateForm(BaseModel):
    schedule: datetime.datetime | None = None

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: datetime.datetime | None) -> datetime.datetime | None:
        """Add timezone info"""
        if v is not None:
            v = v.astimezone(datetime.timezone.utc)
        return v


class EventUpdateForm(
    EventScheduleUpdateForm,
    EvenAddressUpdateForm,
    EvenHostNameUpdateForm,
    EventNewNameUpdateForm,
):
    pass
