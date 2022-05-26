from fastapi import FastAPI
from starlette.responses import RedirectResponse

from paginator import pagination_router

app = FastAPI()


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")


app.include_router(pagination_router, prefix="/pagination", tags=["Pagination"])
