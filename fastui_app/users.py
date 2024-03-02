from http import HTTPStatus
from typing import Annotated

import svcs
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent
from fastui.forms import SelectSearchResponse, fastui_form

from .clients import (  # noqa: F401
    BackendAsyncClient,
    FrontendGetAsyncClient,
    FrontendPostPutDeleteAsyncClient,
)
from .forms import UserCreationForm, UserUpdateForm
from .shared import demo_page
from .utils import _form_user_repr, _raise_for_status

router = APIRouter(include_in_schema=False)


# TODO: Not ready
@router.get("/api/users/search", response_model=SelectSearchResponse)
async def user_ilike_searchview(
    services: svcs.fastapi.DepContainer, name: str | None = None
):
    client = await services.aget(BackendAsyncClient)
    resp = await client.get("/users/search", params={"name": name})
    usernames = resp.json()
    options = [{"label": name, "value": name} for name in usernames]
    return SelectSearchResponse(options=options)


@router.post(
    "/api/users/new/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def user_createview(
    services: svcs.fastapi.DepContainer,
    form: Annotated[UserCreationForm, fastui_form(UserCreationForm)],
):
    client = await services.aget(BackendAsyncClient)
    resp = await client.post("/users", json=form.model_dump())

    # raised, but how to do a full page reload?
    # resp_json = _raise_for_status(resp, HTTPStatus.CREATED)

    if resp.status_code != HTTPStatus.CREATED:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url="/users/"),
                message=f'User not added: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url=f"/users/{form.name}/"))]


@router.get(
    "/api/users/{name}/", response_model=FastUI, response_model_exclude_none=True
)
async def user_detailview(
    services: svcs.fastapi.DepContainer, name: str
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    resp = await client.get("/users", params={"name": name})
    resp_json = _raise_for_status(resp)  # try using prebuilt_html
    user = _form_user_repr(resp_json)
    page_comp_list = [
        c.Heading(text=user.name, level=2),
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=user),
    ]

    # update user button
    modal_comps = [
        c.Button(
            text="Update User",
            on_click=PageEvent(name="update-user"),
            class_name="+ ms-2",
        ),
        c.Modal(
            title="Update User",
            body=[
                c.Paragraph(text=f"Confirm to update User (username={name})"),
                c.ModelForm(
                    model=UserUpdateForm,
                    submit_url=f"/api/users/{name}/update/",
                    loading=[c.Spinner(text="Updating...")],
                    footer=[],
                    submit_trigger=PageEvent(
                        name="modal-form-update-user-submit",
                    ),
                ),
            ],
            footer=[
                c.Button(
                    text="Submit",
                    on_click=PageEvent(name="modal-form-update-user-submit"),
                ),
            ],
            open_trigger=PageEvent(name="update-user"),
        ),
    ]

    # delete user button
    if resp_json["n_events"] == 0:
        modal_comps.extend(
            [
                c.Button(
                    text="Delete User",
                    on_click=PageEvent(name="delete-user"),
                    class_name="+ ms-2",
                ),
                c.Modal(
                    title="Delete User",
                    body=[
                        c.Paragraph(text=f"Confirm to delete User (username={name})"),
                        c.Form(
                            form_fields=[],
                            submit_url=f"/api/users/{name}/delete/",
                            loading=[c.Spinner(text="Deleting...")],
                            footer=[],
                            submit_trigger=PageEvent(name="form-delete-user-submit"),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Submit",
                            on_click=PageEvent(name="form-delete-user-submit"),
                        ),
                    ],
                    open_trigger=PageEvent(name="delete-user"),
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
    "/api/users/{name}/update/", response_model=FastUI, response_model_exclude_none=True
)
async def user_updateview(
    services: svcs.fastapi.DepContainer,
    form: Annotated[UserUpdateForm, fastui_form(UserUpdateForm)],
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    form_dict = {"name": name} | form.model_dump()
    resp = await client.put("/users", json=form_dict)
    if resp.status_code != HTTPStatus.OK:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url=f"/users/{form_dict['name']}/"),
                message=f'User not updated: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url="/users/"))]


@router.post(
    "/api/users/{name}/delete/", response_model=FastUI, response_model_exclude_none=True
)
async def user_deleteview(
    services: svcs.fastapi.DepContainer,
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(BackendAsyncClient)
    resp = await client.delete("/users", params={"name": name})
    if resp.status_code != HTTPStatus.OK:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url=f"/users/{name}/"),
                message=f'User not deleted: {resp_json["detail"]["error"]}',
            )
        ]
    return [c.FireEvent(event=GoToEvent(url="/users/"))]


@router.get("/api/users/", response_model=FastUI, response_model_exclude_none=True)
async def user_listview(
    services: svcs.fastapi.DepContainer,
) -> list[AnyComponent]:
    """
    Show a table of four users, `/api` is the endpoint the frontend will connect to
    when a user visits `/` to fetch components to render.
    """
    client = await services.aget(BackendAsyncClient)
    resp = await client.get("/users")
    resp_json_list = _raise_for_status(resp, HTTPStatus.OK)
    users = [_form_user_repr(resp_json) for resp_json in resp_json_list]
    page_comp_list = [
        c.Heading(text="Users", level=2),
        c.Div(
            components=[
                c.Button(
                    text="Add User",
                    on_click=PageEvent(name="add-user"),
                ),
                c.Modal(
                    title="Add User",
                    body=[
                        c.ModelForm(
                            model=UserCreationForm,
                            submit_url="/api/users/new/",
                            loading=[c.Spinner(text="Adding...")],
                            footer=[],
                            submit_trigger=PageEvent(name="modal-form-add-user-submit"),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Submit",
                            on_click=PageEvent(name="modal-form-add-user-submit"),
                        ),
                    ],
                    open_trigger=PageEvent(name="add-user"),
                ),
            ],
            class_name="mb-3",
        ),
    ]
    if users:
        page_comp_list.append(
            c.Table(
                data=users,
                columns=[
                    DisplayLookup(
                        field="name",
                        on_click=GoToEvent(url="/users/{name}/"),
                    ),
                    DisplayLookup(field="created_at", mode=DisplayMode.date),
                    DisplayLookup(field="n_events", mode=DisplayMode.plain),
                ],
            ),
        )

    return demo_page(*page_comp_list)
