from typing import Annotated
from fastapi import Depends, HTTPException
from .repository import EmployeeRepository, EmployeeRepositoryDep
from .schemes import (
    EmployeeCreateDto,
    EmployeeDeleteDto,
    EmployeeFilters,
    EmployeeResponse,
    EmployeeUpdateDto,
    EmployeePageResponse,
)
from src.core import PageRequest


class EmployeeService:
    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository = repository

    async def create(self, employee: EmployeeCreateDto):
        return await self._repository.create(employee.model_dump())

    async def update(
        self,
        employee_id: int,
        data: EmployeeUpdateDto,
    ) -> EmployeeResponse:
        result = await self._repository.update(employee_id, data.model_dump())
        if result is None:
            raise HTTPException(400, "Employee not found")
        return EmployeeResponse.model_validate(result, from_attributes=True)

    async def delete(self, employee: EmployeeDeleteDto) -> None:
        result = await self._repository.delete(employee.id)
        if not result:
            raise HTTPException(400, "Employee not found")
        return

    async def list(
        self, page_request: PageRequest, filters: EmployeeFilters
    ) -> EmployeePageResponse:
        employees = await self._repository.list(
            filters=filters.model_dump(exclude_unset=True),
            offset=page_request.offset,
            limit=page_request.page_size,
        )
        return EmployeePageResponse(
            items=[
                EmployeeResponse.model_validate(empl, from_attributes=True)
                for empl in employees[0]
            ],
            page_number=page_request.page_number,
            page_size=page_request.page_size,
            total=employees[1],
        )


def get_employee_service(repository: EmployeeRepositoryDep):
    return EmployeeService(repository)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
