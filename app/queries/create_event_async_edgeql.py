# AUTOGENERATED FROM 'app/queries/create_event.edgeql' WITH:
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
class CreateEventResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    address: str | None
    schedule: datetime.datetime | None
    host_name: str


async def create_event(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
    address: str | None,
    schedule: str | None,
    host_name: str,
) -> CreateEventResult:
    return await executor.query_single(
        """\
        with name := <str>$name,
            address := <optional str>$address ?? <str>{},
            schedule := <datetime>(<optional str>$schedule ?? <str>{}),
            host_name := <str>$host_name,
        select (
            insert Event {
                name := name,
                address := address,
                schedule := schedule,
                host := (
                    with u:= assert_single((select User filter .name = host_name)),
                    select 
                    if exists u then (u)
                    else (insert User {name:= host_name})
                )
            }
        ) {name, address, schedule, host_name:=.host.name};\
        """,
        name=name,
        address=address,
        schedule=schedule,
        host_name=host_name,
    )
