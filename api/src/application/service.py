from typing import Any, TypeVar

from httpx import HTTPError

from application.shared.dtos import CreateModelT, UpdateModelT, FiltersModelT
from domain.shared import DomainModelT
from domain.shared.value_objects.id import ID_TYPE
from shared.dtos.page import Page, PageParams
from shared.interfaces.repository import RepositoryProtocol
from shared.interfaces.service import CRUDServiceProtocol


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
        update_model: type[UpdateModelT],
        repository: RepositoryProtocol[DomainModelT, UpdateModelT, Any],
    ) -> None:
        self._update_model = update_model
        self._domain_model = domain_model
        self._repository = repository

    T = TypeVar("T", bound=Any)

    def _unify_to_list(self, data: T | list[T]) -> list[T]:
        if not isinstance(data, list):
            data = [data]
        return data

    async def get_page(
        self,
        filters: FiltersModelT | None,
        page: PageParams,
    ) -> Page[DomainModelT]:
        filters_serialized = filters.model_dump() if filters else None
        return await self._repository.get_page(
            filters=filters_serialized or None,
            page=page,
        )

    async def get_by_id(self, id: Any) -> DomainModelT | None:
        return await self._repository.get_one(filters={"id": id})

    async def get_by_id_or_raise(self, id: Any) -> DomainModelT:
        entity = await self.get_by_id(id)
        if entity is None:
            raise HTTPError(message="Entity not found")
        return entity

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]:
        data = self._unify_to_list(data)
        domain_models = [self._domain_model.model_validate(m) for m in data]
        return await self._repository.create(domain_models)

    async def update(
        self,
        data: UpdateModelT | list[UpdateModelT],
    ) -> list[DomainModelT]:
        unified = self._unify_to_list(data)
        updates = [self._update_model.model_validate(row) for row in unified]
        return await self._repository.update(updates)

    async def delete(self, data: ID_TYPE | list[ID_TYPE]) -> bool:
        data_unified = self._unify_to_list(data)
        return await self._repository.delete(data_unified)
