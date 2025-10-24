from typing import Any, Protocol, Sequence, TypeVar

from .schemes import Page, PageParams
from .domain import DomainModelT
from .repository import AsyncRepositoryProtocol
from pydantic import BaseModel


class CreateDto(BaseModel): ...


class UpdateDto(BaseModel): ...


class FiltersDto(BaseModel):
    id: Any | None = None


CreateModelT = TypeVar("CreateModelT", bound=CreateDto, covariant=True)
UpdateModelT = TypeVar("UpdateModelT", bound=UpdateDto, covariant=True)
FiltersModelT = TypeVar("FiltersModelT", bound=FiltersDto)

T = TypeVar("T", bound=BaseModel)


class CRUDAsyncServiceProtocol(
    Protocol[DomainModelT, CreateModelT, UpdateModelT, FiltersModelT]
):
    """CRUD operations service protocol. Mixin to add basic CRUD interface for domain"""

    def __init__(self, repository: AsyncRepositoryProtocol) -> None: ...

    async def get_list(
        self, filters: FiltersModelT, page: PageParams
    ) -> Page[DomainModelT]: ...
    async def get_one(self, id: Any) -> DomainModelT | None: ...

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]: ...

    async def update(self, data: dict[Any, UpdateModelT]) -> list[DomainModelT]: ...

    async def delete(self, data: Any | list[Any]) -> bool: ...


class CRUDAsyncService(
    CRUDAsyncServiceProtocol[DomainModelT, CreateModelT, UpdateModelT, FiltersModelT]
):
    """
    Generic service for CRUD operations implementation.
    Generics are as follows:
    - DomainModel
    - CreateModel
    - UpdateModel
    - FiltersModel
    """

    def __init__(self, repository: AsyncRepositoryProtocol) -> None:
        self._repository = repository

    def _unify_to_list(self, data: T | list[T]) -> list[T]:
        if not isinstance(data, list):
            data = [data]
        return data

    def _serialize_data(self, data: T | list[T]) -> list[Any]:
        list_data = self._unify_to_list(data)
        return [row.model_dump() for row in list_data]

    async def get_list(
        self,
        filters: FiltersModelT | None,
        page: PageParams,
    ) -> Page[DomainModelT]:
        filters_serialized = filters.model_dump() if filters else None
        return await self._repository.get_list(
            filters=filters_serialized or None,
            page=page,
        )

    async def get_one(self, id: Any) -> DomainModelT | None:
        return await self._repository.get_one(filters={"id": id})

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]:
        return await self._repository.create(self._serialize_data(data))

    async def update(
        self,
        data: dict[Any, UpdateModelT],
    ) -> list[DomainModelT]:
        data_serialized = [(id, update.model_dump()) for id, update in data]
        return await self._repository.update(data_serialized)

    async def delete(self, data: Any | list[Any]) -> bool:
        data_unified = self._unify_to_list(data)
        return await self._repository.delete(data_unified)
