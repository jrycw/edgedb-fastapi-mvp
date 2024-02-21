# AUTOGENERATED FROM 'app/queries/get_events.edgeql' WITH:
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
class GetEventsResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    address: str | None
    schedule: datetime.datetime | None
    host: GetEventsResultHost | None


@dataclasses.dataclass
class GetEventsResultHost(NoPydanticValidation):
    id: uuid.UUID
    name: str


async def get_events(
    executor: edgedb.AsyncIOExecutor,
) -> list[GetEventsResult]:
    return await executor.query(
        """\
        select Event {name, address, schedule, host : {name}};\
        """,
    )
