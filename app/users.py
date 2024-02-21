from __future__ import annotations

from http import HTTPStatus
from typing import Annotated

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, HTTPException, Query

from .models import UserCreate, UserUpdate
from .queries import create_user_async_edgeql as create_user_qry
from .queries import delete_user_async_edgeql as delete_user_qry
from .queries import get_user_by_name_async_edgeql as get_user_by_name_qry
from .queries import get_users_async_edgeql as get_users_qry
from .queries import update_user_async_edgeql as update_user_qry

router = APIRouter()


################################
# Get users
################################


@router.get(
    "/users",
    response_model=list[get_users_qry.GetUsersResult]
    | get_user_by_name_qry.GetUserByNameResult,
)
async def get_users(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    client = await services.aget(AsyncIOClient)
    if name is None:
        return await get_users_qry.get_users(client)
    else:
        if user := await get_user_by_name_qry.get_user_by_name(client, name=name):
            return user

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": f"Username '{name}' does not exist."},
    )


################################
# Create users
################################


@router.post(
    "/users",
    status_code=HTTPStatus.CREATED,
    response_model=create_user_qry.CreateUserResult,
)
async def post_user(services: svcs.fastapi.DepContainer, user: UserCreate):
    client = await services.aget(AsyncIOClient)
    try:
        created_user = await create_user_qry.create_user(client, **user.model_dump())
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": f"Username '{user.name}' already exists."},
        )
    else:
        return created_user


################################
# Update users
################################


@router.put("/users", response_model=update_user_qry.UpdateUserResult)
async def put_user(
    services: svcs.fastapi.DepContainer,
    user: UserUpdate,
):
    client = await services.aget(AsyncIOClient)
    try:
        updated_user = await update_user_qry.update_user(client, **user.model_dump())
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": f"Username '{user.name}' already exists."},
        )
    else:
        if updated_user:
            return updated_user

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": f"User '{user.name}' was not found."},
    )


################################
# Delete users
################################


@router.delete("/users", response_model=delete_user_qry.DeleteUserResult)
async def delete_user(
    services: svcs.fastapi.DepContainer, name: Annotated[str, Query(max_length=50)]
):
    client = await services.aget(AsyncIOClient)
    try:
        deleted_user = await delete_user_qry.delete_user(
            client,
            name=name,
        )
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": "User attached to an event. Cannot delete."},
        )
    else:
        if deleted_user:
            return deleted_user

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": f"User '{name}' was not found."},
    )
