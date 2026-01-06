from application.service import CRUDService
from domain.employee import Employee
from fastapi import Depends
from typing import Annotated
from shared.interfaces.service import CRUDServiceProtocol
from .dtos import EmployeeCreateDto, EmployeeUpdateDto, EmployeeFilters
from infrastructure.repositories.employee import EmployeeRepositoryDep


class EmployeeServiceProtocol(
    CRUDServiceProtocol[Employee, EmployeeCreateDto, EmployeeUpdateDto, EmployeeFilters]
): ...


class EmployeeService(
    EmployeeServiceProtocol,
    CRUDService[Employee, EmployeeCreateDto, EmployeeUpdateDto, EmployeeFilters],
): ...


def get_employee_service(
    employee_repository: EmployeeRepositoryDep,
) -> EmployeeServiceProtocol:
    return EmployeeService(
        Employee,
        employee_repository,
    )


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
