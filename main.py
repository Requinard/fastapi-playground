from fastapi import FastAPI

from paginator import pagination_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(pagination_router, prefix="/pagination", tags=["Pagination"])
