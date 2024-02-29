import datetime
import uuid

from pydantic import BaseModel, Field


################################
# Abstract
################################
class Auditable(BaseModel):
    created_at: datetime.datetime


################################
# User
################################
class UserID(BaseModel):
    id: uuid.UUID


class UserName(BaseModel):
    name: str = Field(title="Username", description="max length: 50", max_length=50)


class UserCreate(UserName):
    pass


class UserNewName(BaseModel):
    new_name: str = Field(
        title="New Username", description="max length: 50", max_length=50
    )


class UserUpdate(UserNewName, UserCreate):
    pass


class UserFull(Auditable, UserCreate, UserID):
    n_events: int


################################
# Event
################################


class EventID(BaseModel):
    id: uuid.UUID


class EventName(BaseModel):
    name: str = Field(title="Eventname", description="max length: 50", max_length=50)


class EventHostName(BaseModel):
    host_name: str | None = Field(
        title="Hostname", description="max length: 50", max_length=50
    )


class EventAddress(BaseModel):
    address: str | None


class EventSchedule(BaseModel):
    schedule: str | None


class EventCreate(EventSchedule, EventAddress, EventHostName, EventName):
    pass


class EventNewName(BaseModel):
    new_name: str | None = Field(
        title="New Eventname", description="max length: 50", max_length=50
    )


class EventUpdate(EventNewName, EventCreate):
    pass


class EventFull(Auditable, EventCreate, EventID):
    pass


################################
# Health
################################
class HealthOut(BaseModel):
    ok: list[str] = Field(default_factory=list)
