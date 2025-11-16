from fastapi import APIRouter

from application.employee.dtos import (
    EmployeeCreateDto,
    EmployeeFiltersDep,
    EmployeeUpdateDto,
    EmployeeResponse,
    EmployeeUpdateDtoBase,
)
from application.employee.service import EmployeeServiceDep
from shared.dtos.page import Page, PageRequestDep
from domain.employee import Employee
from domain.shared import ID_TYPE

router = APIRouter(prefix="/employee", tags=["employee"])


@router.get("/", response_model=Page[EmployeeResponse])
async def list_employees(
    service: EmployeeServiceDep,
    page: PageRequestDep,
    filters: EmployeeFiltersDep,
) -> Page[Employee]:
    return await service.get_page(filters, page)


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    service: EmployeeServiceDep,
    data: EmployeeCreateDto,
) -> Employee:
    return (await service.create([data]))[0]


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_details(
    employee_id: ID_TYPE,
    service: EmployeeServiceDep,
) -> Employee:
    return await service.get_one_or_raise(employee_id)


@router.post("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: ID_TYPE,
    data: EmployeeUpdateDtoBase,
    service: EmployeeServiceDep,
) -> Employee:
    return (
        await service.update(EmployeeUpdateDto(id=employee_id, **data.model_dump()))
    )[0]
