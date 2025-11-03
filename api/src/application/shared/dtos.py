from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from domain.shared import ID_TYPE


class CreateDto(BaseModel): ...


class UpdateDto(BaseModel):
    id: ID_TYPE


class FiltersDto(BaseModel):
    id: ID_TYPE | None = None


class ResponseDto(BaseModel): ...


class Page[T](BaseModel):
    items: list[T]
    page_number: int
    page_size: int
    total: int


class PageParams(BaseModel):
    page_number: int
    page_size: int

    @property
    def offset(self):
        return (self.page_number - 1) * self.page_size


def pagerequest(
    page_number: Annotated[int, Query(ge=1, le=2**32)] = 1,
    page_size: Annotated[int, Query(ge=1, le=1000)] = 10,
) -> PageParams:
    return PageParams(page_number=page_number, page_size=page_size)


PageRequestDep = Annotated[PageParams, Depends(pagerequest)]
