from http import HTTPStatus
from typing import Annotated

import svcs
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent
from fastui.forms import fastui_form

from .clients import (  # noqa: F401
    BackendAsyncClient,
    FrontendGetAsyncClient,
    FrontendPostPutDeleteAsyncClient,
)
from .forms import EventCreationForm, EventUpdateForm
from .shared import demo_page
from .utils import _form_event_repr, _raise_for_status

router = APIRouter(include_in_schema=False)


@router.post(
    "/api/events/new/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def event_createview(
    services: svcs.fastapi.DepContainer,
    form: Annotated[EventCreationForm, fastui_form(EventCreationForm)],
):
    client = await services.aget(BackendAsyncClient)
    form_dict = form.model_dump()
    if s := form_dict["schedule"]:
        form_dict.update(schedule=s.isoformat())
    resp = await client.post("/events", json=form_dict)
    if resp.status_code != HTTPStatus.CREATED:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url="/events/"),
                message=f'Event not added: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url=f"/events/{form.name}/"))]
    # return [c.FireEvent(event=GoToEvent(url="/events/"))]


@router.get(
    "/api/events/{name}/", response_model=FastUI, response_model_exclude_none=True
)
async def event_detailview(
    services: svcs.fastapi.DepContainer, name: str
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    resp = await client.get("/events", params={"name": name})
    resp_json = _raise_for_status(resp)  # try using prebuilt_html
    event = _form_event_repr(resp_json)
    page_comp_list = [
        c.Heading(text=event.name, level=2),
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=event),
    ]

    # update event button
    modal_comps = [
        c.Button(
            text="Update Event",
            on_click=PageEvent(name="update-event"),
            class_name="+ ms-2",
        ),
        c.Modal(
            title="Update Event",
            body=[
                c.Paragraph(text=f"Confirm to update Event (Eventname={name})"),
                c.ModelForm(
                    model=EventUpdateForm,
                    submit_url=f"/api/events/{name}/update/",
                    loading=[c.Spinner(text="Updating...")],
                    footer=[],
                    submit_trigger=PageEvent(name="modal-form-update-event-submit"),
                ),
            ],
            footer=[
                c.Button(
                    text="Submit",
                    on_click=PageEvent(name="modal-form-update-event-submit"),
                ),
            ],
            open_trigger=PageEvent(name="update-event"),
        ),
    ]

    # delete event button
    modal_comps.extend(
        [
            c.Button(
                text="Delete Event",
                on_click=PageEvent(name="delete-event"),
                class_name="+ ms-2",
            ),
            c.Modal(
                title="Delete Event",
                body=[
                    c.Paragraph(text=f"Confirm to delete Event (Eventname={name})"),
                    c.Form(
                        form_fields=[],
                        submit_url=f"/api/events/{name}/delete/",
                        loading=[c.Spinner(text="Deleting...")],
                        footer=[],
                        submit_trigger=PageEvent(name="form-delete-event-submit"),
                    ),
                ],
                footer=[
                    c.Button(
                        text="Submit",
                        on_click=PageEvent(name="form-delete-event-submit"),
                    ),
                ],
                open_trigger=PageEvent(name="delete-event"),
            ),
        ]
    )

    page_comp_list.append(
        c.Div(
            components=modal_comps,
            class_name="mb-3",
        )
    )
    return demo_page(*page_comp_list)


@router.post(
    "/api/events/{name}/update/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def event_updateview(
    services: svcs.fastapi.DepContainer,
    form: Annotated[EventUpdateForm, fastui_form(EventUpdateForm)],
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    form_dict = {"name": name} | form.model_dump()
    if s := form_dict["schedule"]:
        form_dict.update(schedule=s.isoformat())
    resp = await client.put("/events", json=form_dict)
    if resp.status_code != HTTPStatus.OK:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url=f"/events/{form_dict['name']}/"),
                message=f'User not updated: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url="/events/"))]


@router.post(
    "/api/events/{name}/delete/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def event_deleteview(
    services: svcs.fastapi.DepContainer,
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    resp = await client.delete("/events", params={"name": name})
    if resp.status_code != HTTPStatus.OK:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url=f"/events/{name}/"),
                message=f'Event not deleted: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url="/events/"))]


@router.get("/api/events/", response_model=FastUI, response_model_exclude_none=True)
async def event_listview(
    services: svcs.fastapi.DepContainer,
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    resp = await client.get("/events")
    resp_json_list = _raise_for_status(resp, HTTPStatus.OK)
    events = [_form_event_repr(resp_json) for resp_json in resp_json_list]

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
                            model=EventCreationForm,
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
                    # How to handle the rendering issue if host_name is not required?
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
