from typing import Annotated

from fastapi import APIRouter, Body, status

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

router = APIRouter(
    prefix="/employee",
    tags=["Employee Management"],
    responses={
        400: {"description": "Not Found: The requested employee does not exist."},
        500: {
            "description": "Internal Server Error: Something went wrong on the server side."
        },
    },
)


@router.get("/", response_model=EmployeePageResponse)
async def list_employees(
    service: EmployeeServiceDep,
    page: PageRequestDep,
    filters: EmployeeFiltersDep,
):
    return await service.get_list(filters, page)


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreateDto, service: EmployeeServiceDep):
    return await service.create(payload)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdateDto,
    service: EmployeeServiceDep,
):
    return await service.update({employee_id: data})


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, service: EmployeeServiceDep):
    await service.delete(EmployeeDeleteDto(id=employee_id))
    return None
