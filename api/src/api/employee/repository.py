from typing import Annotated
from fastapi import Depends

from core.repository import AsyncRepositoryProtocol
from src.core import AsyncAlchemyRepository
from src.database import DbSessionDep
from src.database import Employee as EmployeeDB
from .domain import Employee


class EmployeeRepositoryProtocol(AsyncRepositoryProtocol[Employee, EmployeeDB]): ...


class EmployeeRepository(
    AsyncAlchemyRepository[Employee, EmployeeDB], EmployeeRepositoryProtocol
):
    pass


def get_employee_repository(db: DbSessionDep) -> EmployeeRepository:
    return EmployeeRepository(Employee, EmployeeDB, db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]
