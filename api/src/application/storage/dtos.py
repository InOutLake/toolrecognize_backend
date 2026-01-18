from typing import Annotated

from fastapi import Depends, Query

from application.shared.dtos import (
    CreateDto,
    FiltersDto,
    ResponseDto,
    UpdateDto,
    UpdateDtoBase,
)
from domain.shared import ID_TYPE


class StorageResponse(ResponseDto):
    id: ID_TYPE
    name: str
    address: str


class StorageCreateDto(CreateDto):
    name: str
    address: str


class StorageUpdateDtoBase(UpdateDtoBase):
    name: str | None = None
    address: str | None = None


class StorageUpdateDto(UpdateDto, StorageUpdateDtoBase): ...


class StorageFilters(FiltersDto):
    name: str | None
    address: str | None


def storage_filters(
    name: Annotated[str | None, Query()] = None,
    address: Annotated[str | None, Query()] = None,
) -> StorageFilters:
    return StorageFilters(name=name, address=address)


StorageFiltersDep = Annotated[StorageFilters, Depends(storage_filters)]
