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
    name: str = Field(max_length=50)


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    new_name: str = Field(max_length=50)


class UserFull(Auditable, UserID, UserBase):
    pass


################################
# Event
################################


class EventID(BaseModel):
    id: uuid.UUID


class EventBase(BaseModel):
    name: str


class EventCreate(EventBase):
    address: str
    schedule: datetime.datetime
    host_name: str = Field(max_length=50)


class EventUpdate(EventCreate):
    new_name: str = Field(max_length=50)


class EventFull(Auditable, EventID, EventCreate):
    pass


################################
# Health
################################
class HealthOut(BaseModel):
    ok: list[str] = Field(default_factory=list)
