from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from application.shared.dtos import CreateDto, FiltersDto, Page, PageParams, UpdateDto
from domain.shared import DomainModelT
from infrastructure.repositories import RepositoryProtocol

CreateModelT = TypeVar("CreateModelT", bound=CreateDto, covariant=True)
UpdateModelT = TypeVar("UpdateModelT", bound=UpdateDto, covariant=True)
FiltersModelT = TypeVar("FiltersModelT", bound=FiltersDto)

T = TypeVar("T", bound=BaseModel)


class CRUDServiceProtocol(
    Protocol[DomainModelT, CreateModelT, UpdateModelT, FiltersModelT]
):
    """CRUD operations service protocol. Mixin to add basic CRUD interface for domain"""

    def __init__(self, repository: RepositoryProtocol[DomainModelT, Any]) -> None: ...

    async def get_page(
        self, filters: FiltersModelT, page: PageParams
    ) -> Page[DomainModelT]: ...
    async def get_one(self, id: Any) -> DomainModelT | None: ...

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]: ...

    async def update(
        self, data: UpdateModelT | list[UpdateModelT]
    ) -> list[DomainModelT]: ...

    async def delete(self, data: Any | list[Any]) -> bool: ...


class CRUDService(
    CRUDServiceProtocol[DomainModelT, CreateModelT, UpdateModelT, FiltersModelT]
):
    """
    Generic service for CRUD operations implementation.
    Generics are as follows:
    - DomainModel
    - CreateModel
    - UpdateModel
    - FiltersModel
    """

    def __init__(
        self,
        domain_model: type[DomainModelT],
        repository: RepositoryProtocol[DomainModelT, Any],
    ) -> None:
        self._domain_model = domain_model
        self._repository = repository

    def _unify_to_list(self, data: T | list[T]) -> list[T]:
        if not isinstance(data, list):
            data = [data]
        return data

    def _serialize_data(self, data: T | list[T]) -> list[Any]:
        list_data = self._unify_to_list(data)
        return [row.model_dump() for row in list_data]

    async def get_page(
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

    async def _update_or_create(self, data: Any) -> list[DomainModelT]:
        data_unified = self._unify_to_list(data)
        domain_models = [
            self._domain_model.model_validate(create_data)
            for create_data in data_unified
        ]
        return await self._repository.save(domain_models)

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]:
        return await self._update_or_create(data)

    async def update(
        self,
        data: UpdateModelT | list[UpdateModelT],
    ) -> list[DomainModelT]:
        return await self._update_or_create(data)

    async def delete(self, data: Any | list[Any]) -> bool:
        data_unified = self._unify_to_list(data)
        return await self._repository.delete(data_unified)
