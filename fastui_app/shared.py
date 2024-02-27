from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent


def _page_title(title: str | None = None) -> AnyComponent:
    return c.PageTitle(text=f"EdgeDB FastUI — {title}" if title else "EdgeDB FastUI")


def _navbar() -> AnyComponent:
    return c.Navbar(
        title="EdgeDB FastUI",
        title_event=GoToEvent(url="/"),
        start_links=[
            c.Link(
                components=[c.Text(text="Users")],
                on_click=GoToEvent(url="/users/"),
                active="startswith:/users",
            ),
            c.Link(
                components=[c.Text(text="Events")],
                on_click=GoToEvent(url="/events/"),
                active="startswith:/events",
            ),
        ],
    )


def _page(components: tuple[AnyComponent], title: str | None = None) -> AnyComponent:
    return c.Page(
        components=[
            *((c.Heading(text=title),) if title else ()),
            *components,
        ],
    )


def _footer() -> AnyComponent:
    return c.Footer(
        extra_text="EdgeDB FastUI",
        links=[
            c.Link(
                components=[c.Text(text="Github")],
                on_click=GoToEvent(url="https://github.com/pydantic/FastUI"),
            ),
            c.Link(
                components=[c.Text(text="PyPI")],
                on_click=GoToEvent(url="https://pypi.org/project/fastui/"),
            ),
            c.Link(
                components=[c.Text(text="NPM")],
                on_click=GoToEvent(url="https://www.npmjs.com/org/pydantic/"),
            ),
        ],
    )


def demo_page(
    *components: AnyComponent, title: str | None = None
) -> list[AnyComponent]:
    return [
        _page_title(title),
        _navbar(),
        _page(components, title),
        _footer(),
    ]
