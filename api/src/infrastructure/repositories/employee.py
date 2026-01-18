from typing import Annotated

from fastapi import Depends

from domain.employee.employee import Employee
from infrastructure.database import Employee as EmployeeDB
from infrastructure.database.database import DbSessionDep
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository
from shared.interfaces.repository import RepositoryProtocol


class EmployeeRepositoryProtocol(RepositoryProtocol): ...


class EmployeeRepository(
    EmployeeRepositoryProtocol, SqlAlchemyRepository[Employee, EmployeeDB]
): ...


def get_employee_repository(session: DbSessionDep) -> EmployeeRepositoryProtocol:
    return EmployeeRepository(Employee, EmployeeDB, session)


EmployeeRepositoryDep = Annotated[
    EmployeeRepositoryProtocol, Depends(get_employee_repository)
]
