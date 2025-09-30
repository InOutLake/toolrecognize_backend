from typing import Annotated

from fastapi import APIRouter, Body

from src.core import PageRequestDep

from .schemes import (
    EmployeeCreateDto,
    EmployeeDeleteDto,
    EmployeeFiltersDep,
    EmployeePageResponse,
    EmployeeResponse,
    EmployeeUpdateDto,
)
from .service import EmployeeServiceDep

router = APIRouter(prefix="/employee", tags=["employee"])


@router.get("/", response_model=EmployeePageResponse)
async def list_employees(
    service: EmployeeServiceDep,
    page: PageRequestDep,
    filters: EmployeeFiltersDep,
):
    return await service.list(page, filters)


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    payload: Annotated[EmployeeCreateDto, Body(embed=False)],
    service: EmployeeServiceDep,
):
    result = await service.create(payload)
    return EmployeeResponse.model_validate(result, from_attributes=True)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdateDto,
    service: EmployeeServiceDep,
):
    return await service.update(employee_id, data)


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: int,
    service: EmployeeServiceDep,
):
    await service.delete(EmployeeDeleteDto(id=employee_id))
    return None
