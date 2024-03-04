from edgedb.asyncio_client import AsyncIOClient
from faker import Faker

fker = Faker()


async def add_users(db_client: AsyncIOClient, target_n_users=5):
    """
    faker.name() might produce the same name. Using `set` to make sure `target_n_users` can be achieved.
    """
    names = set()
    while len(names) < target_n_users:
        names.add(fker.name())

    return await db_client.query(
        """\
        delete Event;
        delete User;
        for name in array_unpack(<array<str>>$names)
        union (insert User {name:= name});\
        """,
        names=list(names),
    )


async def add_events(db_client: AsyncIOClient, target_n_events=5):
    """
    faker.text() might produce the same name. Using `set` to make sure `target_n_events` can be achieved.
    """
    names = set()
    while len(names) < target_n_events:
        names.add(fker.text(max_nb_chars=20).rstrip("."))

    return await db_client.query(
        """\
        with dummy_user:= (insert User {name:= "dummy user"}),
        for name in array_unpack(<array<str>>$names)
        union (insert Event {name:= name, host:= dummy_user });\
        """,
        names=list(names),
    )
