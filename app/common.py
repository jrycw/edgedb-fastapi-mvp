from fastapi import APIRouter

router = APIRouter(include_in_schema=False)


@router.get("/")
async def home():
    return {"message": "Hello World from FastAPI"}
