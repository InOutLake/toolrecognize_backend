from datetime import datetime
from typing import Annotated
from typing import Optional, TypeVar
from fastapi import Depends, Query
from pydantic import BaseModel

ID_TYPE = int


class BaseDto(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class Model(BaseModel):
    id: ID_TYPE


class DtoModel(BaseDto, BaseModel): ...


T = TypeVar("T", bound=BaseModel)


class Page[T](BaseModel):
    items: list[T]
    page_number: int
    page_size: int
    total: int


class PageRequest(BaseModel):
    page_number: int
    page_size: int

    @property
    def offset(self):
        return (self.page_number - 1) * self.page_size


def pagerequest(
    page_number: Annotated[int, Query(ge=1, le=2**32)] = 1,
    page_size: Annotated[int, Query(ge=1, le=1000)] = 10,
) -> PageRequest:
    return PageRequest(page_number=page_number, page_size=page_size)


PageRequestDep = Annotated[PageRequest, Depends(pagerequest)]
