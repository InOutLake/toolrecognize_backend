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


@router.get(
    "/",
    response_model=EmployeePageResponse,
    summary="List employees with pagination and filtering",
    description="""
    Retrieve a paginated list of employees.

    Supports optional filtering by name (case-insensitive substring match) and standard pagination parameters.
    """,
    response_description="A paginated list of employees.",
)
async def list_employees(
    service: EmployeeServiceDep,
    page: PageRequestDep,
    filters: EmployeeFiltersDep,
):
    """
    Endpoint to list employees.

    Args:
        service: Injected employee service for business logic.
        page: Pagination parameters (page number and size).
        filters: Optional filters to narrow down results.

    Returns:
        EmployeePageResponse: Paginated response containing matching employees.
    """
    return await service.list(page, filters)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create a new employee record in the system.",
    response_description="The newly created employee.",
    responses={
        400: {"description": "Bad Request: Invalid input data provided."},
        422: {"description": "Unprocessable Entity: Validation error in request body."},
    },
)
async def create_employee(
    payload: Annotated[
        EmployeeCreateDto,
        Body(
            embed=False,
            description="Employee creation payload.",
            example={"name": "Jane Doe"},
        ),
    ],
    service: EmployeeServiceDep,
):
    """
    Create a new employee.

    Args:
        payload: Employee data to create.
        service: Injected employee service.

    Returns:
        EmployeeResponse: The created employee with assigned ID.
    """
    result = await service.create(payload)
    return EmployeeResponse.model_validate(result, from_attributes=True)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Partially update an employee",
    description="Update one or more fields of an existing employee by ID.",
    response_description="The updated employee.",
    responses={
        400: {"description": "Bad Request: Invalid update data."},
        404: {"description": "Not Found: No employee exists with the given ID."},
        422: {
            "description": "Unprocessable Entity: Validation error in request body or path."
        },
    },
)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdateDto,
    service: EmployeeServiceDep,
):
    """
    Partially update an employee.

    Args:
        employee_id: ID of the employee to update.
        data: Fields to update (partial update).
        service: Injected employee service.

    Returns:
        EmployeeResponse: The updated employee.
    """
    return await service.update(employee_id, data)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
    description="Permanently remove an employee from the system by ID.",
    responses={
        400: {"description": "Bad request data."},
        422: {"description": "Unprocessable Entity: Invalid employee ID format."},
    },
)
async def delete_employee(
    employee_id: int,
    service: EmployeeServiceDep,
):
    """
    Delete an employee.

    Args:
        employee_id: ID of the employee to delete.
        service: Injected employee service.

    Returns:
        None: 204 No Content on successful deletion.
    """
    await service.delete(EmployeeDeleteDto(id=employee_id))
    return None
