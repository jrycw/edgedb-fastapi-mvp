# AUTOGENERATED FROM 'app/queries/search_users_by_name_ilike.edgeql' WITH:
#     $ edgedb-py


from __future__ import annotations
import edgedb


async def search_users_by_name_ilike(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str | None,
) -> list[str]:
    return await executor.query(
        """\
        with name:= <optional str>$name ?? "%",
             name:= "%" ++ <str>$name ++ "%",
             users:= (select User filter .name ilike name),
        select users.name;\
        """,
        name=name,
    )
