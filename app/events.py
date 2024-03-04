from http import HTTPStatus
from typing import Annotated

import edgedb
import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, HTTPException, Query

from .logging import CLogLevel, async_ep_log
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
    tags=["events"],
)
async def get_events(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str | None, Query(max_length=50)] = None,
):
    db_client = await services.aget(AsyncIOClient)
    if name is None:
        return await get_events_qry.get_events(db_client)
    else:
        if event := await get_event_by_name_qry.get_event_by_name(db_client, name=name):
            return event

    err_msg = f"Event '{name}' does not exist."
    await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail={"error": err_msg},
    )


# ################################
# Create events
# ################################


@router.post(
    "/events",
    status_code=HTTPStatus.CREATED,
    response_model=create_event_qry.CreateEventResult,
    tags=["events"],
)
async def post_event(
    services: svcs.fastapi.DepContainer,
    event: EventCreate,
):
    db_client = await services.aget(AsyncIOClient)
    try:
        created_event = await create_event_qry.create_event(
            db_client, **event.model_dump()
        )
    except edgedb.errors.InvalidArgumentError:
        err_msg = """\
                    Invalid datetime format. Datetime string must look like this: \n
                    '2010-12-27T23:59:59-07:00'\
                  """
        await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    except edgedb.errors.ConstraintViolationError:
        err_msg = f"Event name '{event.name}' already exists."
        await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    else:
        return created_event


# ################################
# Update events
# ################################


@router.put(
    "/events",
    response_model=update_event_qry.UpdateEventResult,
    tags=["events"],
)
async def put_event(
    services: svcs.fastapi.DepContainer,
    event: EventUpdate,
):
    db_client = await services.aget(AsyncIOClient)
    try:
        updated_event = await update_event_qry.update_event(
            db_client, **event.model_dump()
        )
    except edgedb.errors.InvalidArgumentError:
        err_msg = """\
                    Invalid datetime format. Datetime string must look like this: \n
                    '2010-12-27T23:59:59-07:00'\
                  """
        await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    except edgedb.errors.ConstraintViolationError:
        err_msg = f"Event name '{event.name}' already exists."
        await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"error": err_msg},
        )
    else:
        if updated_event:
            return updated_event

    err_msg = f"Update event '{event.name}' failed."
    await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={"error": err_msg},
    )


# ################################
# Delete events
# ################################


@router.delete(
    "/events",
    response_model=delete_event_qry.DeleteEventResult,
    tags=["events"],
)
async def delete_event(
    services: svcs.fastapi.DepContainer,
    name: Annotated[str, Query(max_length=50)],
):
    db_client = await services.aget(AsyncIOClient)
    if deleted_event := await delete_event_qry.delete_event(db_client, name=name):
        return deleted_event

    err_msg = f"Delete event '{name}' failed."
    await async_ep_log("api.events", err_msg, CLogLevel.WARNING)
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={"error": err_msg},
    )
