from fastapi import APIRouter, Depends
from starlette.requests import Request


def with_auditing(request: Request):
    yield None

    print(f"AUDIT\t {request.client.host}")


auditing_router = APIRouter()


@auditing_router.get("/", dependencies=[Depends(with_auditing)])
def get_audited_hello():
    return "Hello"
