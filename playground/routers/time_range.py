from datetime import datetime
from typing import Optional, List, TypeVar, Callable

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, select, Session
from sqlmodel.sql.expression import SelectOfScalar

from playground.providers.database import get_session

time_range_router = APIRouter()


class TimeRangedModel(SQLModel, table=True):
    id: Optional[int] = Field(None, primary_key=True)
    comment: str = Field(...)
    date_created: datetime = Field(..., sa_column=Column(DateTime))


T = TypeVar('T')


def with_timerange(time_from: Optional[datetime] = Query(None, description="The minimum datetime of items to include"),
                   time_to: Optional[datetime] = Query(None, description="The maximum datetime of items to include")):
    def apply_timerange(column, query: SelectOfScalar[T]):
        if time_to:
            query = query.where(column <= time_to)

        if time_from:
            query = query.where(column >= time_from)

        return query

    return apply_timerange


def with_paginator(page: int = Query(0, ge=0), page_size: int = Query(100, ge=0, le=1000)) -> Callable[[SelectOfScalar[T]], SelectOfScalar[T]]:
    def apply_pagination(query: SelectOfScalar[T]):
        return query.limit(page_size).offset(page_size * page)

    return apply_pagination


@time_range_router.get("/", response_model=List[TimeRangedModel], tags=["Pagination"])
def get_comments(session: Session = Depends(get_session), apply_timerange=Depends(with_timerange), paginator=Depends(with_paginator)):
    comments_query = apply_timerange(TimeRangedModel.date_created, select(TimeRangedModel))
    comments_query = paginator(comments_query)

    return session.exec(comments_query).all()


@time_range_router.post("/")
def create_test_comments(session: Session = Depends(get_session)):
    for i in range(10):
        comment = TimeRangedModel(
            comment=f"Comment {i}",
            date_created=datetime.now(),
        )

        session.add(comment)

    session.commit()
