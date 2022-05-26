import math
from functools import lru_cache
from typing import Callable, TypeVar, List

from fastapi import Query, APIRouter, Depends
from pydantic.generics import GenericModel, Generic

pagination_router = APIRouter()
PaginatedType = TypeVar("PaginatedType")

PAGINATED_SIZE = 1000


class PaginatedResult(GenericModel, Generic[PaginatedType]):
    page: int
    page_size: int
    page_count: int

    data: List[PaginatedType]


def with_paginator(page: int = Query(0, ge=0), page_size: int = Query(100, ge=0, le=1000)) -> Callable[
    [List[PaginatedType]], PaginatedResult[PaginatedType]]:
    def paginate(items: List[PaginatedType]) -> PaginatedResult[PaginatedType]:
        start_item = page_size * page
        end_item = start_item + page_size

        return PaginatedResult(
            page=page,
            page_size=page_size,
            page_count=math.floor(len(items) / page_size),
            data=items[start_item:end_item]
        )

    return paginate


@lru_cache
def get_example_list():
    return list(range(0, PAGINATED_SIZE))


@pagination_router.get("/unpaginated", response_model=List[int])
def get_unpaginated():
    return get_example_list()


@pagination_router.get("/paginated", response_model=PaginatedResult[int])
def get_paginated(paginator=Depends(with_paginator)):
    l = get_example_list()

    return paginator(l)
