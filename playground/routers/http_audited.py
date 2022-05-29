import asyncio
from typing import Optional, List, AsyncGenerator

import httpx
import starlette
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.requests import Request

from playground.routers.http_authorized import a_raise_on_4xx_5xx


class AuditMessage(BaseModel):
    source_host: str
    destination_host: str
    path: str
    success: bool
    extra_message: Optional[str] = None


class Auditor:
    """
    A basic implementation of an auditing resource. It should be instantiated once per request.

    During a request, messages can be added to the auditor. At the end of a session, the auditor will flush all messages.
    """

    def __init__(self, audit_name: str = "Audit"):
        self.messages: List[AuditMessage] = []
        self.audit_name = audit_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for message in self.messages:
            print(
                f"AUDIT ({self.audit_name}) {'SUCCESS' if message.success else 'FAILED'} - {message.source_host} to {message.destination_host} - {message.extra_message}"
            )

    def add_message(self, message: AuditMessage):
        self.messages.append(message)

    def add_starlette_request(self, request: starlette.requests.Request, success: bool):
        message = AuditMessage(
            source_host=request.client.host,
            destination_host=request.url.hostname,
            path=request.url.path,
            extra_message="Initial request",
            success=success,
        )

        self.add_message(message)


def audit_httpx_request(auditor: Auditor):
    async def inner(response: httpx.Response):
        request = response.request
        message = AuditMessage(
            source_host=request.url.host,
            destination_host=response.url.host,
            path=request.url.path,
            success=200 <= response.status_code < 300,
        )

        auditor.add_message(message)

    return inner


class AuditedWebClient:
    """
    Returns a webclient that automatically audits the incoming and outgoing request.

    It even handles errors, setting the audit state to 0
    """

    def __init__(self, name: str):
        self.name = name

    async def __call__(
        self, request: Request
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        with Auditor(self.name) as auditor:

            async with httpx.AsyncClient(follow_redirects=True) as client:
                client.event_hooks["response"] = [
                    audit_httpx_request(auditor),
                    a_raise_on_4xx_5xx,
                ]

                try:
                    yield client
                    auditor.add_starlette_request(request, True)
                except Exception as e:
                    auditor.add_starlette_request(request, False)

                    raise e


http_audited_router = APIRouter()


@http_audited_router.get("/success")
async def http_audited_passthrough_success(
    client: httpx.AsyncClient = Depends(AuditedWebClient("AUDIT_SUCCESS")),
):
    await asyncio.gather(
        client.get("https://google.com"),
        client.get("https://ifconfig.me/ip"),
        return_exceptions=True,
    )

    return "Success"


@http_audited_router.get("/fail", status_code=422)
async def http_audited_passthrough_fail(
    client: httpx.AsyncClient = Depends(AuditedWebClient("AUDIT_FAIL")),
):
    await asyncio.gather(
        client.get("https://google.com"),
        client.get("https://ifconfig.me/ip"),
        return_exceptions=True,
    )

    raise HTTPException(status_code=422, detail="This should fail")
