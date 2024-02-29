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


class UserBase(BaseModel):
    name: str = Field(title="Username", description="max length: 50", max_length=50)


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    new_name: str = Field(
        title="New Username", description="max length: 50", max_length=50
    )


class UserFull(Auditable, UserBase, UserID):
    pass


class UserRepr(UserFull):
    n_events: int


################################
# Event
################################


class EventID(BaseModel):
    id: uuid.UUID


class EventBase(BaseModel):
    name: str = Field(title="Eventname", description="max length: 50", max_length=50)


class EventCreate(EventBase):
    host_name: str | None = Field(
        title="Hostname", description="max length: 50", max_length=50
    )
    address: str | None
    schedule: str | None


class EventUpdate(EventCreate):
    new_name: str | None = Field(
        title="New Eventname", description="max length: 50", max_length=50
    )


class EventFull(Auditable, EventCreate, EventID):
    pass


class EventRepr(EventFull):
    pass


################################
# Health
################################
class HealthOut(BaseModel):
    ok: list[str] = Field(default_factory=list)
