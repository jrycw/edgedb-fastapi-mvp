from fastapi import (
    APIRouter,
    HTTPException,  # noqa: F401
)
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.events import BackEvent, GoToEvent, PageEvent  # noqa:F401

from .models import EventFull, UserFull  # noqa: F401
from .shared import demo_page
from .utils import _raise_for_status  # noqa: F401

router = APIRouter(include_in_schema=False)


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def home() -> list[AnyComponent]:
    return demo_page(
        c.Heading(text="Home", level=1), c.Paragraph(text="Hello World from FastUI")
    )


@router.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React router, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))
