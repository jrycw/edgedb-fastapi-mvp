from __future__ import annotations

import datetime  # noqa: F401
from http import HTTPStatus
from typing import Annotated

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, HTTPException, Query

from .models import EventCreate, EventUpdate
from .queries import create_event_async_edgeql as create_event_qry
from .queries import delete_event_async_edgeql as delete_event_qry
from .queries import get_event_by_name_async_edgeql as get_event_by_name_qry
from .queries import get_events_async_edgeql as get_events_qry
from .queries import update_event_async_edgeql as update_event_qry

router = APIRouter()


################################
# Get events
################################


@router.get(
    "/events",
    response_model=list[get_events_qry.GetEventsResult]
    | get_event_by_name_qry.GetEventByNameResult,
)
async def get_events(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    client = await services.aget(AsyncIOClient)
    if name is None:
        return await get_events_qry.get_events(client)
    else:
        if event := await get_event_by_name_qry.get_event_by_name(client, name=name):
            return event

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": f"Event '{name}' does not exist."},
    )


# ################################
# Create events
# ################################


@router.post(
    "/events",
    status_code=HTTPStatus.CREATED,
    response_model=create_event_qry.CreateEventResult,
)
async def post_event(
    services: svcs.fastapi.DepContainer,
    event: EventCreate,
):
    client = await services.aget(AsyncIOClient)
    try:
        created_event = await create_event_qry.create_event(
            client, **event.model_dump()
        )
    except edgedb.errors.InvalidArgumentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={
                "error": "Invalid datetime format. "
                "Datetime string must look like this: "
                "'2010-12-27T23:59:59-07:00'",
            },
        )
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": f"Event name '{event.name}' already exists."},
        )
    else:
        return created_event


# ################################
# Update events
# ################################


@router.put("/events", response_model=update_event_qry.UpdateEventResult)
async def put_event(
    services: svcs.fastapi.DepContainer,
    event: EventUpdate,
):
    client = await services.aget(AsyncIOClient)
    try:
        updated_event = await update_event_qry.update_event(
            client, **event.model_dump()
        )
    except edgedb.errors.InvalidArgumentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={
                "error": "Invalid datetime format. "
                "Datetime string must look like this: '2010-12-27T23:59:59-07:00'",
            },
        )
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": f"Event name '{event.name}' already exists."},
        )
    else:
        if updated_event:
            return updated_event
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={"error": f"Update event '{event.name}' failed."},
    )


# ################################
# Delete events
# ################################


@router.delete("/events", response_model=delete_event_qry.DeleteEventResult)
async def delete_event(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str, Query(max_length=50)],
):
    client = await services.aget(AsyncIOClient)
    if deleted_event := await delete_event_qry.delete_event(client, name=name):
        return deleted_event

    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={"error": f"Delete event '{name}' failed."},
    )
