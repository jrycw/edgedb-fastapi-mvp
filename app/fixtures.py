import json
from http import HTTPStatus
from typing import Annotated

import svcs
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, Body

from .factories import gen_event
from .models import DevDataCreate
from .queries import create_event_async_edgeql as create_event_qry
from .queries import prepare_dev_data_async_edgeql as prepare_dev_data_qry

router = APIRouter(include_in_schema=False)


@router.post(
    "/fixtures",
    status_code=HTTPStatus.OK,
    response_model=list[create_event_qry.CreateEventResult],
    tags=["fixtures"],
)
async def prepare_dev_data(
    services: svcs.fastapi.DepContainer,
    dev_data: Annotated[DevDataCreate, Body()] = DevDataCreate(),
):
    """
    The endpoint is enabled for dev purpose only.
    `prepare_dev_data_qry.prepare_dev_data` will **DELETE ALL USERS AND EVENTS**!!!
    Well, after all, this is a setup for dev.
    """
    client = await services.aget(AsyncIOClient)
    data = [
        gen_event().model_dump(include={"name", "address", "schedule", "host_name"})
        for _ in range(dev_data.n)
    ]
    return await prepare_dev_data_qry.prepare_dev_data(client, data=json.dumps(data))
