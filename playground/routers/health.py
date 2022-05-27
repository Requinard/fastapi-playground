from fastapi import APIRouter, Depends

from playground.providers.database import get_session

health_router = APIRouter()


@health_router.get("/health", dependencies=[Depends(get_session)])
async def get_health():
    return "OK"


@health_router.get("/ping")
async def get_ping():
    return "pong"
