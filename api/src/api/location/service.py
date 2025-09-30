from typing import Annotated
from fastapi import Depends, HTTPException
from .repository import LocationRepository, LocationRepositoryDep
from .schemes import (
    LocationCreateDto,
    LocationDeleteDto,
    LocationFilters,
    LocationResponse,
    LocationUpdateDto,
    LocationPageResponse,
)
from src.core import PageRequest


class LocationService:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def create(self, location: LocationCreateDto):
        return await self._repository.create(location.model_dump())

    async def update(
        self, location_id: int, data: LocationUpdateDto
    ) -> LocationResponse:
        result = await self._repository.update(location_id, data.model_dump())
        if result is None:
            raise HTTPException(400, "Location not found")
        return LocationResponse.model_validate(result, from_attributes=True)

    async def delete(self, location: LocationDeleteDto) -> None:
        result = await self._repository.delete(location.id)
        if not result:
            raise HTTPException(400, "Location not found")
        return

    async def list(
        self, page_request: PageRequest, filters: LocationFilters
    ) -> LocationPageResponse:
        locations = await self._repository.list(
            filters=filters.model_dump(exclude_unset=True),
            offset=page_request.offset,
            limit=page_request.page_size,
        )
        return LocationPageResponse(
            items=[
                LocationResponse.model_validate(loc, from_attributes=True)
                for loc in locations[0]
            ],
            page_number=page_request.page_number,
            page_size=page_request.page_size,
            total=locations[1],
        )


def get_location_service(repository: LocationRepositoryDep):
    return LocationService(repository)


LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
