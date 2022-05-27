from fastapi import APIRouter, Depends

from playground.providers.database import get_session

health_router = APIRouter()


@health_router.get("/health", dependencies=[Depends(get_session)])
async def get_health():
    """
    Health endpoint that returns if the application can connect to all its services. If it does not return, the app cannot take requests nor connect to a database.

    It depends on a database session. If the session is present, the health check is ok. If the session cannot be started, the health check has failed.

    It should be used as a readyness-check.
    """
    return "OK"


@health_router.get("/ping")
async def get_ping():
    """
    Health endpoint that should always return. If it does not return, the application can not accept any requests.

    It should be used as a liveness-check.
    """
    return "pong"
