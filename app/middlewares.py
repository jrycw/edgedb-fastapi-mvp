import time

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from uvicorn.protocols.utils import get_path_with_query_string


async def add_logging_middleware(request: Request, call_next) -> Response:
    api_access_logger = structlog.stdlib.get_logger("backend.access")
    structlog.contextvars.clear_contextvars()
    request_id = correlation_id.get()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    start_time = time.perf_counter_ns()

    response = Response(status_code=500)
    try:
        response = await call_next(request)
    except Exception:
        structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        url = get_path_with_query_string(request.scope)

        # request.client is None for tests, so we need to fill in something here
        client_host = getattr(request.client, "host", "testing_client_host")
        client_port = getattr(request.client, "port", "testing_client_port")

        http_method = request.method
        http_version = request.scope["http_version"]
        api_access_logger.info(
            f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
            http={
                "url": str(request.url),
                "status_code": status_code,
                "method": http_method,
                "request_id": request_id,
                "version": http_version,
            },
            network={"client": {"ip": client_host, "port": client_port}},
            duration=process_time,
        )
        response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response
