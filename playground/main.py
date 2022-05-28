import time

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from msgpack_asgi import MessagePackMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from playground.routers.auditing import auditing_router
from playground.routers.auth_passthrough import auth_passthrough_router
from playground.routers.health import health_router
from playground.routers.paginator import pagination_router
from playground.routers.time_range import time_range_router

# Create the app and apply some middleware
app = FastAPI(default_response_class=ORJSONResponse)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(MessagePackMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Measure request execution time and add it to the response as a header.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """
    Automatically redirect a user to the docs.
    """
    return RedirectResponse("/docs")


# Add the individual routers
app.include_router(pagination_router, prefix="/pagination", tags=["Pagination"])
app.include_router(time_range_router, prefix="/timeranged", tags=["Time Range"])
app.include_router(auditing_router, prefix="/auditing", tags=["Auditing"])
app.include_router(
    auth_passthrough_router, prefix="/auth-passthrough", tags=["Auth", "HTTP"]
)
app.include_router(health_router, prefix="/health", tags=["Health"])
