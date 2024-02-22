from __future__ import annotations

from http import HTTPStatus

import svcs
from fastapi import APIRouter, HTTPException

from .models import HealthOut

router = APIRouter()


async def _check_healthy(
    services: svcs.fastapi.DepContainer,
) -> tuple[list[str], list[dict[str, str]]]:
    ok: list[str] = []
    failing: list[dict[str, str]] = []

    for svc in services.get_pings():
        try:
            await svc.aping()
            ok.append(svc.name)
        except Exception as e:
            failing.append({svc.name: repr(e)})

    return ok, failing


@router.get(
    "/healthy",
    response_model=HealthOut,
    status_code=HTTPStatus.OK,
    tags=["health"],
)
async def healthy(services: svcs.fastapi.DepContainer):
    """
    Ping all external services.
    ref: https://svcs.hynek.me/en/stable/integrations/fastapi.html
    """
    ok, failing = await _check_healthy(services)

    if not failing:
        return {"ok": ok}

    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail={"error": f"Health check failed: {failing}"},  # better rendering?
    )
