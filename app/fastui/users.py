from http import HTTPStatus  # noqa: F401
from typing import Annotated  # noqa: F401

import svcs
from edgedb.asyncio_client import AsyncIOClient  # noqa: F401
from fastapi import (
    APIRouter,  # noqa: F401
    HTTPException,  # noqa: F401
)
from fastapi.responses import HTMLResponse  # noqa: F401
from fastui import AnyComponent, FastUI, prebuilt_html  # noqa: F401
from fastui import components as c  # noqa: F401
from fastui.components.display import DisplayLookup, DisplayMode  # noqa: F401
from fastui.events import BackEvent, GoToEvent, PageEvent  # noqa:F401
from fastui.forms import fastui_form  # noqa: F401
from httpx import AsyncClient  # noqa: F401

from ..models import UserFull  # noqa: F401
from .forms import UserCreationForm, UserUpdateForm  # noqa: F401
from .queries.check_user_deletable_async_edgeql import (
    check_user_deletable,  # noqa: F401
)
from .shared import demo_page  # noqa: F401
from .utils import _raise_for_status  # noqa: F401

router = APIRouter()


@router.get("/api/users/new/", response_model=FastUI, response_model_exclude_none=True)
async def display_add_user():
    return demo_page(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
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
                event=GoToEvent(url="/users/new/"),
                message=f'USER Exists: {resp_json["detail"]["error"]}',
            ),
            c.ModelForm(
                model=UserCreationForm,
                display_mode="page",
                submit_url="/api/users/new/",
            ),
        ]
    return [c.FireEvent(event=GoToEvent(url=f"/users/{form.name}/"))]


@router.get(
    "/api/users/{name}/", response_model=FastUI, response_model_exclude_none=True
)
async def user_profile(
    services: svcs.fastapi.DepContainer, name: str
) -> list[AnyComponent]:
    """
    User profile page, the frontend will fetch this when the user visits `/users/{id}/`.
    """
    client = await services.aget(AsyncClient)
    resp = await client.get("/users", params={"name": name})
    resp_json = _raise_for_status(resp, HTTPStatus.OK)
    user = UserFull(**resp_json)

    page_comp_list = [
        c.Heading(text=user.name, level=2),
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=user),
        c.Div(
            components=[
                c.Button(
                    text="Update User",
                    on_click=PageEvent(name="modal-update-prompt"),
                    class_name="+ ms-2",
                ),
                c.Modal(
                    title="Form Prompt",
                    body=[
                        c.Paragraph(text=f"Confirm to update User(username={name})"),
                        c.ModelForm(
                            model=UserUpdateForm,
                            submit_url=f"/api/users/{name}/update/",
                            loading=[c.Spinner(text="Updating...")],
                            footer=[],
                            submit_trigger=PageEvent(name="modal-form-update-submit"),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Cancel",
                            named_style="secondary",
                            on_click=PageEvent(name="modal-update-prompt", clear=True),
                        ),
                        c.Button(
                            text="Submit",
                            on_click=PageEvent(name="modal-form-update-submit"),
                        ),
                    ],
                    open_trigger=PageEvent(name="modal-update-prompt"),
                ),
            ],
            class_name="mb-3",
        ),
    ]

    db_client = await services.aget(AsyncIOClient)
    if await check_user_deletable(db_client, name=name):
        page_comp_list.append(
            c.Div(
                components=[
                    c.Button(
                        text="Delete User",
                        on_click=PageEvent(name="modal-delete-prompt"),
                        class_name="+ ms-2",
                    ),
                    c.Modal(
                        title="Form Prompt",
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
                                    name="modal-form-delete-submit"
                                ),
                            ),
                        ],
                        footer=[
                            c.Button(
                                text="Cancel",
                                named_style="secondary",
                                on_click=PageEvent(
                                    name="modal-delete-prompt", clear=True
                                ),
                            ),
                            c.Button(
                                text="Submit",
                                on_click=PageEvent(name="modal-form-delete-submit"),
                            ),
                        ],
                        open_trigger=PageEvent(name="modal-delete-prompt"),
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
    resp_json = _raise_for_status(resp, HTTPStatus.OK)
    return [c.FireEvent(event=GoToEvent(url=f"/users/{form_dict['new_name']}/"))]


@router.post(
    "/api/users/{name}/delete/", response_model=FastUI, response_model_exclude_none=True
)
async def delete_user(
    services: svcs.fastapi.DepContainer,
    name: str,
) -> list[AnyComponent]:
    """
    User profile page, the frontend will fetch this when the user visits `/users/{id}/`.
    """
    client = await services.aget(AsyncClient)
    resp = await client.delete("/users", params={"name": name})
    if resp.status_code != HTTPStatus.OK:
        resp_json = resp.json()
        return [
            c.FireEvent(
                event=GoToEvent(url=f"/users/{name}/"),
                message=f'USER Exists: {resp_json["detail"]["error"]}',
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
                c.Link(
                    components=[c.Button(text="Add User")],
                    on_click=GoToEvent(url="/users/new/"),
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
