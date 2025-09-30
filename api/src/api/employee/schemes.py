from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel
from src.core import BaseDto, Model, Page


class EmployeeResponse(BaseDto, Model):
    name: str


class EmployeePageResponse(Page[EmployeeResponse]): ...


class EmployeeFilters(BaseModel):
    name: str | None = None


def employee_filters(
    name: Annotated[str | None, Query()] = None,
) -> EmployeeFilters:
    return EmployeeFilters(name=name)


EmployeeFiltersDep = Annotated[EmployeeFilters, Depends(employee_filters)]


class EmployeeCreateDto(BaseModel):
    name: str


class EmployeeUpdateDto(BaseModel):
    name: str | None = None


class EmployeeDeleteDto(Model): ...
