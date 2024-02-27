from http import HTTPStatus
from typing import Annotated

import svcs
from fastapi import (
    APIRouter,
    HTTPException,  # noqa: F401
)
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent, PageEvent  # noqa:F401
from fastui.forms import fastui_form
from httpx import AsyncClient

from .forms import UserCreationForm, UserUpdateForm
from .models import UserFull
from .shared import demo_page
from .utils import _raise_for_status  # noqa: F401

router = APIRouter(include_in_schema=False)


@router.get("/api/users/new/", response_model=FastUI, response_model_exclude_none=True)
async def display_add_user():
    return demo_page(
        c.Heading(text="Add User", level=2),
        c.Paragraph(text="Add a user to the system"),
        c.ModelForm(
            model=UserCreationForm,
            display_mode="page",
            submit_url="/api/users/new/",
        ),
    )


@router.post(
    "/api/users/new/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def post_user(
    services: svcs.fastapi.DepContainer,
    form: Annotated[UserCreationForm, fastui_form(UserCreationForm)],
):
    client = await services.aget(AsyncClient)
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
async def user_profile(
    services: svcs.fastapi.DepContainer, name: str
) -> list[AnyComponent]:
    client = await services.aget(AsyncClient)
    resp = await client.get("/internal/users", params={"name": name})  # get n_events
    resp_json = _raise_for_status(resp)  # try using prebuilt_html
    user = UserFull(**resp_json)
    page_comp_list = [
        c.Heading(text=user.name, level=2),
        c.Link(components=[c.Text(text="Back")], on_click=GoToEvent(url="/users/")),
        c.Details(data=user),
        c.Div(
            components=[
                c.Button(
                    text="Update User",
                    on_click=PageEvent(name="update-user"),
                    class_name="+ ms-2",
                ),
                c.Modal(
                    title="Update User",
                    body=[
                        c.Paragraph(text=f"Confirm to update User(username={name})"),
                        c.ModelForm(
                            model=UserUpdateForm,
                            submit_url=f"/api/users/{name}/update/",
                            loading=[c.Spinner(text="Updating...")],
                            footer=[],
                            submit_trigger=PageEvent(
                                name="modal-form-update-user-submit"
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
            ],
            class_name="mb-3",
        ),
    ]
    if resp_json["n_events"] == 0:
        page_comp_list.append(
            c.Div(
                components=[
                    c.Button(
                        text="Delete User",
                        on_click=PageEvent(name="delete-user"),
                        class_name="+ ms-2",
                    ),
                    c.Modal(
                        title="Delete User",
                        body=[
                            c.Paragraph(
                                text=f"Confirm to delete User(username={name})"
                            ),
                            c.Form(
                                form_fields=[],
                                submit_url=f"/api/users/{name}/delete/",
                                loading=[c.Spinner(text="Deleting...")],
                                footer=[],
                                submit_trigger=PageEvent(
                                    name="form-delete-user-submit"
                                ),
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
                ],
            ),
        )
    return demo_page(*page_comp_list)


@router.post(
    "/api/users/{name}/update/", response_model=FastUI, response_model_exclude_none=True
)
async def update_user(
    services: svcs.fastapi.DepContainer,
    form: Annotated[UserUpdateForm, fastui_form(UserUpdateForm)],
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(AsyncClient)
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
    return [c.FireEvent(event=GoToEvent(url=f"/users/{form_dict['new_name']}/"))]


@router.post(
    "/api/users/{name}/delete/", response_model=FastUI, response_model_exclude_none=True
)
async def delete_user(
    services: svcs.fastapi.DepContainer,
    name: str,
) -> list[AnyComponent]:
    client = await services.aget(AsyncClient)
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
async def users_table(
    services: svcs.fastapi.DepContainer,
) -> list[AnyComponent]:
    """
    Show a table of four users, `/api` is the endpoint the frontend will connect to
    when a user visits `/` to fetch components to render.
    """
    client = await services.aget(AsyncClient)
    resp = await client.get("/users")
    resp_json = _raise_for_status(resp, HTTPStatus.OK)
    users = [UserFull(**user) for user in resp_json]
    return demo_page(
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
        c.Table(
            data=users,
            columns=[
                DisplayLookup(
                    field="name",
                    on_click=GoToEvent(url="/users/{name}/"),
                ),
                DisplayLookup(field="id", mode=DisplayMode.auto),
                DisplayLookup(field="created_at", mode=DisplayMode.date),
            ],
        ),
    )


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def home() -> list[AnyComponent]:
    return demo_page(
        c.Heading(text="Home", level=1),
    )


@router.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React router, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))
