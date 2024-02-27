from http import HTTPStatus

import svcs
from fastapi import (
    APIRouter,
    HTTPException,  # noqa: F401
)
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent  # noqa:F401
from httpx import AsyncClient

from .forms import UserCreationForm
from .models import EventRepr  # noqa: F401
from .shared import demo_page
from .utils import _raise_for_status  # noqa: F401

router = APIRouter(include_in_schema=False)


@router.get("/api/events/", response_model=FastUI, response_model_exclude_none=True)
async def events_table(
    services: svcs.fastapi.DepContainer,
) -> list[AnyComponent]:
    client = await services.aget(AsyncClient)
    resp = await client.get("/events")
    resp_json = _raise_for_status(resp, HTTPStatus.OK)
    events = []
    for event in resp_json:
        event.update(host_name=event["host"]["name"])
        del event["host"]
        events.append(EventRepr(**event))
    page_comp_list = [
        c.Heading(text="Events", level=2),
        c.Div(
            components=[
                c.Button(
                    text="Add Event",
                    on_click=PageEvent(name="add-event"),
                ),
                c.Modal(
                    title="Add Event",
                    body=[
                        c.ModelForm(
                            model=UserCreationForm,
                            submit_url="/api/events/new/",
                            loading=[c.Spinner(text="Adding...")],
                            footer=[],
                            submit_trigger=PageEvent(
                                name="modal-form-add-event-submit"
                            ),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Submit",
                            on_click=PageEvent(name="modal-form-add-event-submit"),
                        ),
                    ],
                    open_trigger=PageEvent(name="add-event"),
                ),
            ],
            class_name="mb-3",
        ),
    ]
    if events:
        page_comp_list.append(
            c.Table(
                data=events,
                columns=[
                    DisplayLookup(
                        field="name",
                        on_click=GoToEvent(url="/events/{name}/"),
                    ),
                    DisplayLookup(
                        field="host_name",
                        on_click=GoToEvent(url="/users/{host_name}/"),
                    ),
                    DisplayLookup(field="address", mode=DisplayMode.auto),
                    DisplayLookup(field="schedule", mode=DisplayMode.date),
                    DisplayLookup(field="created_at", mode=DisplayMode.date),
                ],
            ),
        )
    return demo_page(*page_comp_list)
