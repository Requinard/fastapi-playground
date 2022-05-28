import math
from functools import lru_cache
from typing import Callable, TypeVar, List

from fastapi import Query, APIRouter, Depends
from pydantic.generics import GenericModel, Generic

PaginatedType = TypeVar("PaginatedType")

PAGINATED_SIZE = 1000


class PaginatedResult(GenericModel, Generic[PaginatedType]):
    """
    A wrapped around `PaginatedType` that provides page information.
    """

    page: int
    page_size: int
    page_count: int

    data: List[PaginatedType]


PaginatorFunction = Callable[[List[PaginatedType]], PaginatedResult[PaginatedType]]


def with_paginator(
    page: int = Query(0, ge=0, le=1_000_000), page_size: int = Query(100, ge=1, le=1000)
) -> PaginatorFunction:
    """
    A FastAPI dependency that paginates in-memory data sources. It uses dependencies to automatically get the params from the request.

    This paginator is generic and can be added to any endpoint that returns a list.

    :param page: The page you want to get. Starts at 0. Should be greater than or equal to 0.
    :param page_size: The size of the pages you want to get. Defaults to 100. Must be larger than 1 and less than or equal to 1000.
    :return: A function that takes a list of `PaginatedType` and paginates it in memory. This function then returns the `PaginatedResult`.
    """

    def paginate(items: List[PaginatedType]) -> PaginatedResult[PaginatedType]:
        start_item = page_size * page
        end_item = start_item + page_size

        return PaginatedResult(
            page=page,
            page_size=page_size,
            page_count=math.floor(len(items) / page_size),
            data=items[start_item:end_item],
        )

    return paginate


pagination_router = APIRouter()


@lru_cache
def get_example_list() -> List[int]:
    """
    Generate a list of numbers to use as an example.
    :return: A list of numbers
    """
    return list(range(0, PAGINATED_SIZE))


@pagination_router.get("/unpaginated", response_model=List[int])
def get_unpaginated() -> List[int]:
    """
    Get the `example_list` and return it without pagination.
    """
    return get_example_list()


@pagination_router.get("/paginated", response_model=PaginatedResult[int])
def get_paginated(
    paginator: PaginatorFunction = Depends(with_paginator),
) -> PaginatedResult[int]:
    """
    Get the `example_list` and paginate it with the pagination dependency.

    Notice that we do not need to individually get the page parameters here. It is all managed by `with_paginator`
    """
    example_list = get_example_list()

    return paginator(example_list)
