from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel
from src.core import BaseDto, Model, Page

from src.core import CreateDto, UpdateDto, FiltersDto


class EmployeeResponse(BaseModel):
    name: str


class EmployeePageResponse(Page[EmployeeResponse]): ...


class EmployeeCreateDto(CreateDto):
    name: str


class EmployeeUpdate(BaseModel):
    name: str | None = None


class EmployeeUpdateDto(UpdateDto):
    data: EmployeeUpdate


class EmployeeFilters(FiltersDto):
    name: str | None = None


def employee_filters(
    id: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
) -> EmployeeFilters:
    return EmployeeFilters(id=id, name=name)


EmployeeFiltersDep = Annotated[EmployeeFilters, Depends(employee_filters)]


class EmployeeDeleteDto(Model): ...
