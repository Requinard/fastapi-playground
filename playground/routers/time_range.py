from datetime import datetime
from typing import Optional, List, TypeVar, Callable, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from playground.providers.database_async import get_session

time_range_router = APIRouter()


class TimeRangedModel(SQLModel, table=True):
    """
    A SQLModel that can be inserted into a database. Any database will work as SQLAlchemy will take care of the implementation specifics.
    """

    id: Optional[int] = Field(None, primary_key=True, le=2**8)
    comment: str = Field(...)
    date_created: datetime = Field(..., sa_column=Column(DateTime))


T = TypeVar("T")

TimerangeFilterFunction = Callable[[Any, SelectOfScalar[T]], SelectOfScalar[T]]


def with_timerange(
    time_from: Optional[datetime] = Query(
        None, description="The minimum datetime of items to include"
    ),
    time_to: Optional[datetime] = Query(
        None, description="The maximum datetime of items to include"
    ),
) -> TimerangeFilterFunction:
    """
    A FastAPI dependency to generically filter on a date column.

    It uses Query-params to create the filters. If a param is empty, it will not be applied.

    It is generic and can this be used for any table that has a single datetime field to filter with.

    :param time_from: Earliest datetime to be included in the results.
    :param time_to: Latest datetime to be included in the results.
    :return: A function to apply time filters. Call it on a SQLAlchemy expression to add the filters.
    """

    def apply_timerange(column, query: SelectOfScalar[T]) -> SelectOfScalar[T]:
        """
        :param column: Column of `T` that can be filtered as a datetime.
        :param query: The actual SQLAlchemy query that has not yet been executed.
        :return: The query with time filters applied.
        """
        if time_to:
            query = query.where(column <= time_to)

        if time_from:
            query = query.where(column >= time_from)

        return query

    return apply_timerange


PaginatorFilterFunction = Callable[[SelectOfScalar[T]], SelectOfScalar[T]]


def with_paginator(
    page: int = Query(0, ge=0, le=2**8), page_size: int = Query(100, ge=0, le=1000)
) -> PaginatorFilterFunction:
    """
    A FastAPI dependency to apply pagination via the SQL query. See `playground.paginator.with_paginator` for more details.

    It is generic and can be used to paginate any SQL query.
    """

    def apply_pagination(query: SelectOfScalar[T]) -> SelectOfScalar[T]:
        """
        Apply pagination to the SQL query.
        :param query: An existing query that we want to paginate.
        :return: The query with pagination applied.
        """
        return query.limit(page_size).offset(page_size * page)

    return apply_pagination


@time_range_router.get("/", response_model=List[TimeRangedModel], tags=["Pagination"])
async def get_comments(
    session: AsyncSession = Depends(get_session),
    apply_timerange=Depends(with_timerange),
    paginator=Depends(with_paginator),
):
    """
    Get a list of all `TimeRangedModels`. It uses an async database engine and is non-blocking.

    Filtering and pagination are applied by the dependencies.

    :param session: Async database session to use for queries
    :param apply_timerange: Function to add time filtering to a query.
    :param paginator: Function to add pagination to a query.
    :return: All comments that match the filters.
    """
    query = select(TimeRangedModel)
    query = apply_timerange(TimeRangedModel.date_created, query)
    query = paginator(query)

    result = await session.exec(query)

    return result.all()


@time_range_router.post("/")
async def create_test_comments(session: AsyncSession = Depends(get_session)):
    """ "
    Create a set of `TimeRangedModels` as an example.
    """
    for i in range(10):
        comment = TimeRangedModel(
            comment=f"Comment {i}",
            date_created=datetime.now(),
        )

        session.add(comment)

    await session.commit()


class ModelCreateSerializer(BaseModel):
    comment: str = Field(..., min_length=3)


@time_range_router.post("/create", response_model=TimeRangedModel)
async def create_new(
    model: ModelCreateSerializer, session: AsyncSession = Depends(get_session)
):
    time_model = TimeRangedModel(comment=model.comment, date_created=datetime.now())

    session.add(time_model)

    await session.commit()
    await session.refresh(time_model)

    return time_model
