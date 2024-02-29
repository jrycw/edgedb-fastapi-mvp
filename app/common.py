from fastapi import APIRouter, Request

router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request):
    client_host = request.client.host
    return {"message": "Hello World from FastAPI", "client_host": client_host}
