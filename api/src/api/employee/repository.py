from typing import Annotated
from fastapi import Depends

from src.core import AsyncRepository
from src.database import DbSessionDep, Employee


class EmployeeRepository(AsyncRepository[Employee]):
    pass


def get_employee_repository(db: DbSessionDep) -> EmployeeRepository:
    return EmployeeRepository(Employee, db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]
