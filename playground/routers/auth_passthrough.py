import httpx
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request


def raise_on_4xx_5xx(response: httpx.Response):
    """
    Evaluate a `httpx.Response`. In case of an error, it will re-emit the error as a `fastapi.HTTPException`. This lets FastAPI forward the error to the client.

    This method is blocking. It can be used in both regular and async functions. However, it should not be used in async functions due to said blocking.
    """
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Upstream request failed",
                "upstream_request": str(e.request),
            },
        ) from e


async def a_raise_on_4xx_5xx(response: httpx.Response):
    """
    Evaluate a `httpx.Response`. In case of an error, it will re-emit the error as a `fastapi.HTTPException`. This lets FastAPI forward the error to the client.

    This method is non-blocking. It can only be used in async functions. Running in sync is possible but should be avoided.
    """
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Upstream request failed",
                "upstream_request": str(response.request),
            },
        ) from e


def with_http_client(request: Request) -> httpx.Client:
    """
    A FastAPI dependency that creates a HTTP client to call other services.

    It automatically inserts the clients `Authorization`, allowing us to act on behalf of a user.

    This method is blocking. It can be used in both regular and async functions. However, it should not be used in async functions due to said blocking.
    """
    headers = {}

    if auth := request.headers.get("authorization"):
        headers["Authorization"] = auth

    with httpx.Client(headers=headers) as client:
        client.event_hooks["response"] = [raise_on_4xx_5xx]
        yield client


async def with_ahttp_client(request: Request) -> httpx.AsyncClient:
    """
    A FastAPI dependency that creates a HTTP client to call other services.

    It automatically inserts the clients `Authorization`, allowing us to act on behalf of a user.

    This method is non-blocking. It can only be used in async functions. Running in sync is possible but should be avoided.
    """
    headers = {}

    if auth := request.headers.get("authorization"):
        headers["Authorization"] = auth

    async with httpx.AsyncClient(
        headers=headers,
    ) as client:
        client.event_hooks["response"] = [a_raise_on_4xx_5xx]
        yield client


auth_passthrough_router = APIRouter()


@auth_passthrough_router.get("/sync")
def get_ip_sync(client: httpx.Client = Depends(with_http_client)):
    """
    Get the server IP with the clients `Authorization` header.

    This method is blocking.
    """
    ip = client.get("https://ifconfig.me/ip")
    return {"ip": ip.text, "auth_token": client.headers.get("Authorization")}


@auth_passthrough_router.get("/async")
async def get_ip_async(client: httpx.AsyncClient = Depends(with_ahttp_client)):
    """
    Get the server IP with the clients `Authorization` header.

    This method is non-blocking.
    """
    ip = await client.get("https://ifconfig.me/ip")

    return {"ip": ip.text, "auth_token": client.headers.get("Authorization")}
