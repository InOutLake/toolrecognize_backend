from typing import Annotated
from fastapi import Depends, HTTPException

from src.core import CRUDAsyncServiceProtocol, CRUDAsyncService
from .domain import Employee
from .repository import EmployeeRepositoryDep, EmployeeRepositoryProtocol
from .schemes import (
    EmployeeCreateDto,
    EmployeeFilters,
    EmployeeUpdateDto,
)


class EmployeeServiceProtocol(
    CRUDAsyncServiceProtocol[
        Employee, EmployeeCreateDto, EmployeeUpdateDto, EmployeeFilters
    ]
):
    def __init__(self, repository: EmployeeRepositoryProtocol): ...


class EmployeeService(
    EmployeeServiceProtocol,
    CRUDAsyncService[Employee, EmployeeCreateDto, EmployeeUpdateDto, EmployeeFilters],
): ...


def get_employee_service(repository: EmployeeRepositoryDep):
    return EmployeeService(repository)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
