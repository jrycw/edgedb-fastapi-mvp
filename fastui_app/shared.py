from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent


def demo_page(
    *components: AnyComponent, title: str | None = None
) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"EdgeDB FastUI — {title}" if title else "EdgeDB FastUI"),
        c.Navbar(
            title="EdgeDB FastUI",
            title_event=GoToEvent(url="/"),
            start_links=[
                c.Link(
                    components=[c.Text(text="users")],
                    on_click=GoToEvent(url="/users/"),
                    active="startswith:/users",
                ),
            ],
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(
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
        ),
    ]
