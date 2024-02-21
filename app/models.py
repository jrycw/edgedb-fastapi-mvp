import datetime

from pydantic import UUID4, BaseModel


################################
# Abstract
################################
class Auitable(BaseModel):
    created_at: datetime.datetime


################################
# User
################################
class UserID(BaseModel):
    id: UUID4


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    new_name: str


class UserFull(Auitable, UserID, UserBase):
    pass


################################
# Event
################################


class EventID(BaseModel):
    id: UUID4


class EventBase(BaseModel):
    name: str


class EventCreate(EventBase):
    address: str
    schedule: datetime.datetime
    host_name: str


class EventUpdate(EventCreate):
    new_name: str


class EventFull(Auitable, EventID, EventCreate):
    pass
