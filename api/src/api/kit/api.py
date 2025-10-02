from typing import Annotated
from fastapi import APIRouter, Body, status

from .schemes import (
    KitCreateDto,
    KitDeleteDto,
    KitFiltersDep,
    KitPageResponse,
    KitResponse,
    KitUpdateDto,
)
from .service import KitServiceDep
from src.core import PageRequestDep

router = APIRouter(
    prefix="/kit",
    tags=["Kit Management"],
    responses={
        400: {"description": "Bad request data."},
        500: {
            "description": "Internal Server Error: An unexpected error occurred on the server."
        },
    },
)


@router.get(
    "/",
    response_model=KitPageResponse,
    summary="List kits",
    description=(
        "Retrieve a paginated list of kits. "
        "Optionally filter by name or description using query parameters."
    ),
    response_description="A paginated list of kits.",
    responses={
        422: {
            "description": "Unprocessable Entity: Validation error in the request body."
        },
    },
)
async def list_kits(
    service: KitServiceDep,
    page: PageRequestDep,
    filters: KitFiltersDep,
):
    return await service.list(page, filters)


@router.post(
    "/",
    response_model=KitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new kit",
    description="Create a new kit with the provided name and optional description.",
    response_description="The newly created kit.",
    responses={
        400: {
            "description": "Bad Request: Invalid input data (e.g., missing required fields)."
        },
        422: {
            "description": "Unprocessable Entity: Validation error in the request body."
        },
    },
)
async def create_kit(
    payload: Annotated[KitCreateDto, Body(embed=False)],
    service: KitServiceDep,
):
    result = await service.create(payload)
    return KitResponse.model_validate(result, from_attributes=True)


@router.patch(
    "/{kit_id}",
    response_model=KitResponse,
    summary="Partially update a kit",
    description=(
        "Update one or more fields of an existing kit by its ID. "
        "Only the provided fields will be updated; others remain unchanged."
    ),
    response_description="The updated kit.",
    responses={
        400: {"description": "Not Found: No kit exists with the given ID."},
        422: {"description": "Unprocessable Entity: Invalid kit ID or request body."},
    },
)
async def update_kit(
    kit_id: int,
    data: KitUpdateDto,
    service: KitServiceDep,
):
    return await service.update(kit_id, data)


@router.delete(
    "/{kit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a kit",
    description="Permanently delete a kit by its ID.",
    responses={
        400: {"description": "Not Found: No kit exists with the given ID."},
        422: {"description": "Unprocessable Entity: Invalid kit ID format."},
    },
)
async def delete_kit(
    kit_id: int,
    service: KitServiceDep,
):
    await service.delete(KitDeleteDto(id=kit_id))
    return None
