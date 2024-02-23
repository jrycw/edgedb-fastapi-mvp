import svcs
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent
from httpx import AsyncClient

from ..models import UserFull as User

router = APIRouter()


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def users_table(
    services: svcs.fastapi.DepContainer,
) -> list[AnyComponent]:
    """
    Show a table of four users, `/api` is the endpoint the frontend will connect to
    when a user visits `/` to fetch components to render.
    """
    client = await services.aget(AsyncClient)
    users = await client.get("/users")
    users = [User(**user) for user in users.json()]
    return [
        c.Page(
            components=[
                c.Heading(text="Users", level=2),
                c.Table(
                    data=users,
                    columns=[
                        DisplayLookup(
                            field="name",
                            on_click=GoToEvent(url="/user/{name}/"),
                        ),
                        DisplayLookup(field="id", mode=DisplayMode.auto),
                        DisplayLookup(field="created_at", mode=DisplayMode.date),
                    ],
                ),
            ]
        ),
    ]


@router.get(
    "/api/user/{name}/", response_model=FastUI, response_model_exclude_none=True
)
async def user_profile(
    services: svcs.fastapi.DepContainer, name: str
) -> list[AnyComponent]:
    """
    User profile page, the frontend will fetch this when the user visits `/user/{id}/`.
    """
    client = await services.aget(AsyncClient)
    user = await client.get("/users", params={"name": name})
    user = User(**user.json())
    return [
        c.Page(
            components=[
                c.Heading(text=user.name, level=2),
                c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
                c.Details(data=user),
            ]
        ),
    ]


@router.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React router, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))
