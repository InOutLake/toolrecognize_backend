from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.repository import AsyncRepository
from src.database.database import DbSessionDep, Employee


class EmployeeRepository(AsyncRepository[Employee]):
    pass


def get_employee_repository(db: DbSessionDep) -> EmployeeRepository:
    return EmployeeRepository(Employee, db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]
