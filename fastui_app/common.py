from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c

from .shared import demo_page

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
