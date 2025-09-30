from typing import Annotated
from fastapi import APIRouter, Body
from .schemes import (
    LocationCreateDto,
    LocationDeleteDto,
    LocationFiltersDep,
    LocationPageResponse,
    LocationResponse,
    LocationUpdateDto,
)
from .service import LocationServiceDep
from src.core import PageRequestDep

router = APIRouter(prefix="/location", tags=["location"])


@router.get("/", response_model=LocationPageResponse)
async def list_locations(
    service: LocationServiceDep,
    page: PageRequestDep,
    filters: LocationFiltersDep,
):
    return await service.list(page, filters)


@router.post("/", response_model=LocationResponse, status_code=201)
async def create_location(
    payload: Annotated[LocationCreateDto, Body(embed=False)],
    service: LocationServiceDep,
):
    result = await service.create(payload)
    return LocationResponse.model_validate(result, from_attributes=True)


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    data: LocationUpdateDto,
    service: LocationServiceDep,
):
    return await service.update(location_id, data)


@router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: int,
    service: LocationServiceDep,
):
    await service.delete(LocationDeleteDto(id=location_id))
    return None
