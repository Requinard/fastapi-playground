from datetime import datetime, timedelta
from typing import Optional, List, TypeVar

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, select, Session
from sqlmodel.sql.expression import SelectOfScalar

from playground.providers.database import get_session

time_range_router = APIRouter()

T = TypeVar("T")


class TimeRangedModel(SQLModel, table=True):
    id: Optional[int] = Field(None, primary_key=True)
    comment: str = Field(...)
    date_created: datetime = Field(..., sa_column=Column(DateTime))


def with_timerange(time_from: Optional[datetime] = Query(None, description="The minimum datetime of items to include"),
                   time_to: Optional[datetime] = Query(None, description="The maximum datetime of items to include")):
    def apply_timerange(column, query: SelectOfScalar[T]):
        if time_to:
            query = query.where(column <= time_to)

        if time_from:
            query = query.where(column >= time_from)

        return query

    return apply_timerange


@time_range_router.get("/", response_model=List[TimeRangedModel])
def get_comments(session: Session = Depends(get_session), apply_timerange=Depends(with_timerange)):
    comments_query = apply_timerange(TimeRangedModel.date_created, select(TimeRangedModel))

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
