from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request


class Auditer:
    """
    This class allows us to add messages. When the audit context finishes, we can clean up and send messages where they need to go.
    """

    def __init__(self, request: Request, audit_name: str = "Audit"):
        self.messages: List[str] = ["started"]
        self.request = request
        self.audit_name = audit_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for message in self.messages:
            print(f"AUDIT ({self.audit_name}) - CLIENT {self.request.client.host}:{self.request.client.port} - HOST: {self.request.url} - {message}")

    def add_message(self, message: str):
        self.messages.append(message)

    def success(self):
        self.messages.append("request succeeded")

    def failed(self):
        self.messages.append("request_failed")


class ParamaterizedAuditer:
    """
    An auditer that allows us to get some extra params in. This way we can make a specific auditer
    """

    def __init__(self, audit_name: str = "Unknown"):
        self.audit_name = audit_name

    def __call__(self, request: Request) -> Auditer:
        with Auditer(request, self.audit_name) as auditer:
            yield auditer
            auditer.success()


auditing_router = APIRouter()


@auditing_router.get("/manual")
def auditing_with_manual_messages(auditer=Depends(ParamaterizedAuditer("manual"))):
    """
    This endpoint allows us to manually add messages to the auditer.
    """
    auditer.add_message("test")
    auditer.add_message("test 2")
    return {
        "hello": "world"
    }


@auditing_router.get("/automatic", dependencies=[Depends(ParamaterizedAuditer("automatic"))])
def auditing_with_automatic_messages():
    """
    This endpoint will automatically use the auditer without needing to add any messages.
    """
    return {
        "hello": "world"
    }
