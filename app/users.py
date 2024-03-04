from http import HTTPStatus
from typing import Annotated

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, HTTPException, Query

from .logging import CLogLevel, async_ep_log
from .models import UserCreate, UserUpdate
from .queries import create_user_async_edgeql as create_user_qry
from .queries import delete_user_async_edgeql as delete_user_qry
from .queries import get_user_by_name_async_edgeql as get_user_by_name_qry
from .queries import get_users_async_edgeql as get_users_qry
from .queries import (
    search_users_by_name_ilike_async_edgeql as search_users_by_name_ilike_qry,
)
from .queries import update_user_async_edgeql as update_user_qry

router = APIRouter()

################################
# Search users
################################


@router.get(
    "/users/search",
    response_model=list[str],
    tags=["users"],
)
async def search_users_ilike(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    db_client = await services.aget(AsyncIOClient)
    return await search_users_by_name_ilike_qry.search_users_by_name_ilike(
        db_client, name=name
    )


################################
# Get users
################################


@router.get(
    "/users",
    response_model=list[get_users_qry.GetUsersResult]
    | get_user_by_name_qry.GetUserByNameResult,
    tags=["users"],
)
async def get_users(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    db_client = await services.aget(AsyncIOClient)
    if name is None:
        return await get_users_qry.get_users(db_client)
    else:
        if user := await get_user_by_name_qry.get_user_by_name(db_client, name=name):
            return user

    err_msg = f"Username '{name}' does not exist."
    await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": err_msg},
    )


################################
# Create users
################################


@router.post(
    "/users",
    status_code=HTTPStatus.CREATED,
    response_model=create_user_qry.CreateUserResult,
    tags=["users"],
)
async def post_user(services: svcs.fastapi.DepContainer, user: UserCreate):
    db_client = await services.aget(AsyncIOClient)
    try:
        return await create_user_qry.create_user(db_client, **user.model_dump())
    except edgedb.errors.ConstraintViolationError:
        err_msg = f"Username '{user.name}' already exists."
        await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )


################################
# Update users
################################


@router.put(
    "/users",
    response_model=update_user_qry.UpdateUserResult,
    tags=["users"],
)
async def put_user(
    services: svcs.fastapi.DepContainer,
    user: UserUpdate,
):
    db_client = await services.aget(AsyncIOClient)

    try:
        updated_user = await update_user_qry.update_user(db_client, **user.model_dump())
    except edgedb.errors.ConstraintViolationError:
        err_msg = f"Username '{user.name}' already exists."
        await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    else:
        if updated_user:
            return updated_user

    err_msg = f"User '{user.name}' was not found."
    await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": err_msg},
    )


################################
# Delete users
################################


@router.delete(
    "/users",
    response_model=delete_user_qry.DeleteUserResult,
    tags=["users"],
)
async def delete_user(
    services: svcs.fastapi.DepContainer, name: Annotated[str, Query(max_length=50)]
):
    db_client = await services.aget(AsyncIOClient)
    try:
        deleted_user = await delete_user_qry.delete_user(
            db_client,
            name=name,
        )
    except edgedb.errors.ConstraintViolationError:
        err_msg = "User attached to an event. Cannot delete."
        await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    else:
        if deleted_user:
            return deleted_user

    err_msg = f"User '{name}' was not found."
    await async_ep_log("api.users", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": err_msg},
    )
