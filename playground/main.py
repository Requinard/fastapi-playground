from fastapi import FastAPI
from starlette.responses import RedirectResponse

from playground.routers.paginator import pagination_router
from playground.routers.time_range import time_range_router

app = FastAPI()


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")


app.include_router(pagination_router, prefix="/pagination", tags=["Pagination"])
app.include_router(time_range_router, prefix="/timeranged", tags=["Time Range"])