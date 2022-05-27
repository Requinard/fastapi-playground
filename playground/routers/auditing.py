from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request


class Auditer:
    """
    This class allows us to add messages. When the audit context finishes, we can clean up and send messages where they need to go.
    """
    def __init__(self, request: Request):
        self.messages: List[str] = []
        self.request = request

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for message in self.messages:
            print(f"AUDIT - CLIENT {self.request.client.host}:{self.request.client.port} - HOST: {self.request.url} - {message}")

    def add_message(self, message: str):
        self.messages.append(message)


def with_auditing(request: Request) -> Auditer:
    with Auditer(request) as auditer:
        yield auditer


auditing_router = APIRouter()


@auditing_router.get("/", dependencies=[Depends(with_auditing)])
def get_audited_hello(auditer = Depends(with_auditing)):
    auditer.add_message("test")
    auditer.add_message("test 2")
    return "Hello"
