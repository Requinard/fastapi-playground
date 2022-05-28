from typing import List

from fastapi import APIRouter, Depends
from starlette.requests import Request


class Auditor:
    """
    A basic implementation of an auditing resource. It should be instantiated once per request.

    During a request, messages can be added to the auditor. At the end of a session, the auditor will flush all messages.
    """

    def __init__(self, request: Request, audit_name: str = "Audit"):
        self.messages: List[str] = ["started"]
        self.request = request
        self.audit_name = audit_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for message in self.messages:
            print(
                f"AUDIT ({self.audit_name}) - CLIENT {self.request.client.host}:{self.request.client.port} - HOST: {self.request.url} - {message}"
            )

    def add_message(self, message: str):
        self.messages.append(message)

    def success(self):
        self.messages.append("request succeeded")

    def failed(self):
        self.messages.append("request_failed")


class ParamaterizedAuditor:
    """
    Create an object that can instantiate an `Auditor` for FastAPI with pre-applied variables.
    """

    def __init__(self, audit_name: str = "Unknown"):
        """
        The class initializer. We use it to store variables.
        :param audit_name: Name of the audited resource
        """
        self.audit_name = audit_name

    def __call__(self, request: Request) -> Auditor:
        """
        This turns the Parameterized Auditor into an actual auditor. It is called by FastAPI internally.
        :param request: A `starlette.Request` that FastAPI will inject into this `Auditor`
        :return: An auditor to use for auditing trails
        """
        with Auditor(request, self.audit_name) as auditer:
            yield auditer
            auditer.success()


auditing_router = APIRouter()


@auditing_router.get("/manual")
async def auditing_with_manual_messages(
    auditor=Depends(ParamaterizedAuditor("manual")),
):
    """
    An endpoint that manually calls the auditor to add messages
    """
    auditor.add_message("test")
    auditor.add_message("test 2")

    return {"hello": "world"}


@auditing_router.get(
    "/automatic", dependencies=[Depends(ParamaterizedAuditor("automatic"))]
)
async def auditing_with_automatic_messages():
    """
    An endpoint that uses an `Auditor` without manually adding messages to it. It will still log some actions.
    """
    return {"hello": "world"}
