from __future__ import annotations

from http import HTTPStatus

import svcs
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/healthy", include_in_schema=False)
async def healthy(services: svcs.fastapi.DepContainer) -> JSONResponse:
    """
    Ping all external services.
    ref: https://svcs.hynek.me/en/stable/integrations/fastapi.html
    """
    ok: list[str] = []
    failing: list[dict[str, str]] = []
    status_code = HTTPStatus.OK

    for svc in services.get_pings():
        try:
            await svc.aping()
            ok.append(svc.name)
        except Exception as e:
            failing.append({svc.name: repr(e)})
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return JSONResponse(content={"ok": ok, "failing": failing}, status_code=status_code)
