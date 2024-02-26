import datetime  # noqa: F401
import uuid  # noqa: F401

from pydantic import BaseModel, Field  # noqa: F401


class UserCreationForm(BaseModel):
    name: str = Field(title="Username", description="max length: 50", max_length=50)


# class UserDeletionForm(BaseModel):
#     confirm: bool = False


class UserUpdateForm(BaseModel):
    new_name: str = Field(
        title="New Username", description="max length: 50", max_length=50
    )


################################
# Event
################################


################################
# Health
################################
