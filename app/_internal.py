from http import HTTPStatus  # noqa: F401
from typing import Annotated  # noqa: F401

import svcs  # noqa: F401
from edgedb.asyncio_client import AsyncIOClient  # noqa: F401
from fastapi import APIRouter, HTTPException, Query  # noqa: F401

from .queries import (
    get_user_by_name_with_n_events_async_edgeql as get_user_by_name_with_n_events_qry,  # noqa: F401
)
from .queries import get_user_with_n_events_async_edgeql as get_user_with_n_events_qry

router = APIRouter()


@router.get(
    "/internal/users",
    response_model=list[get_user_with_n_events_qry.GetUserWithNEventsResult]
    | get_user_by_name_with_n_events_qry.GetUserByNameWithNEventsResult,
    tags=["_internal"],
)
async def _get_users(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    client = await services.aget(AsyncIOClient)
    if name is None:
        return await get_user_with_n_events_qry.get_user_with_n_events(client)
    else:
        if (
            user
            := await get_user_by_name_with_n_events_qry.get_user_by_name_with_n_events(
                client, name=name
            )
        ):
            return user

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": f"Username '{name}' does not exist."},
    )
