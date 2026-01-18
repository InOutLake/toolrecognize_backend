from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, ConfigDict, EmailStr

from application.shared.dtos import CreateDto, FiltersDto, ResponseDto, UpdateDto
from domain.shared import ID_TYPE
from shared.dtos import Page


class EmployeeResponse(ResponseDto):
    id: ID_TYPE
    first_name: str
    last_name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class EmployeePageResponse(Page[EmployeeResponse]): ...


class EmployeeCreateDto(CreateDto):
    first_name: str
    last_name: str
    email: EmailStr


class EmployeeUpdateDtoBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class EmployeeUpdateDto(UpdateDto, EmployeeUpdateDtoBase): ...


class EmployeeFilters(FiltersDto):
    first_name: str | None
    last_name: str | None
    email: EmailStr | None


def employee_filters(
    first_name: Annotated[str | None, Query()] = None,
    last_name: Annotated[str | None, Query()] = None,
    email: Annotated[str | None, Query()] = None,
) -> EmployeeFilters:
    return EmployeeFilters(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )


EmployeeFiltersDep = Annotated[EmployeeFilters, Depends(employee_filters)]
