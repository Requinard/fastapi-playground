import httpx
from fastapi import APIRouter, Depends
from starlette.requests import Request


def with_http_client(request: Request) -> httpx.Client:
    """
    Creates a new HTTP client with the incoming authorization injected. This lets us masquerade as a user to other services.
    """
    headers = {}

    if auth := request.headers.get("authorization"):
        headers['Authorization'] = auth

    with httpx.Client(headers=headers) as client:
        yield client


async def with_ahttp_client(request: Request) -> httpx.AsyncClient:
    """
    Creates a new HTTP client with the incoming authorization injected. This lets us masquerade as a user to other services.
    """
    headers = {}

    if auth := request.headers.get("authorization"):
        headers['Authorization'] = auth

    async with httpx.AsyncClient(headers=headers) as client:
        yield client


auth_passthrough_router = APIRouter()


@auth_passthrough_router.get("/sync")
def get_for_client(client: httpx.Client = Depends(with_http_client)):
    """
    Use the passthrough client to make requests
    """
    ip = client.get("https://ifconfig.me/ip")
    return {
        "ip": ip.text,
        "auth_token": client.headers.get("Authorization")
    }


@auth_passthrough_router.get("/async")
async def get_async(client: httpx.AsyncClient = Depends(with_ahttp_client)):
    ip = await client.get("https://ifconfig.me/ip")

    return {
        "ip": ip.text,
        "auth_token": client.headers.get("Authorization")
    }
