# AUTOGENERATED FROM 'app/queries/delete_user.edgeql' WITH:
#     $ edgedb-py


from __future__ import annotations
import dataclasses
import datetime
import edgedb
import uuid


class NoPydanticValidation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        # Pydantic 2.x
        from pydantic_core.core_schema import any_schema

        return any_schema()

    @classmethod
    def __get_validators__(cls):
        # Pydantic 1.x
        from pydantic.dataclasses import dataclass as pydantic_dataclass

        pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class DeleteUserResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    created_at: datetime.datetime


async def delete_user(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
) -> DeleteUserResult | None:
    return await executor.query_single(
        """\
        select (
            delete User filter .name = <str>$name
        ) {name, created_at};\
        """,
        name=name,
    )
